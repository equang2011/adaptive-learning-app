import json
import os
from pathlib import Path

from app.clients.gateway import invoke_gateway
from app.models.curriculum import Curriculum, CurriculumNode
from app.models.lesson import (
    DetailLevel,
    Lesson,
    LessonContinuation,
    LessonStart,
    PaginatedLesson,
)
from utils.prompt_builder import build_prompt, compose_prompts, load_prompt

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts"

LEGACY_PROMPT_FILE = os.getenv(
    "LEGACY_LESSON_PROMPT_FILE",
    "lesson_v1.7.md",
)
LESSON_PROMPT_VERSION = os.getenv("LESSON_PROMPT_VERSION", "v1")

SHARED_PROMPT_FILE = f"lesson_shared_{LESSON_PROMPT_VERSION}.md"
PAGE1_PROMPT_FILE = f"lesson_page1_{LESSON_PROMPT_VERSION}.md"
CONTINUATION_PROMPT_FILE = f"lesson_continue_{LESSON_PROMPT_VERSION}.md"

EXPECTED_TOTAL_PAGES: dict[DetailLevel, set[int]] = {
    "quick": {1},
    "standard": {2, 3},
    "deep": {3},
}

def generate_lesson(
    model: str,
    curriculum: Curriculum,
    node: CurriculumNode,
    optional_context: str = "",
) -> Lesson:
    if node.children:
        raise ValueError("Lesson generation requires a leaf node.")
    prompt_template = load_prompt(PROMPT_DIR, LEGACY_PROMPT_FILE)
    curriculum_json = curriculum.model_dump_json(indent=2)
    node_json = node.model_dump_json(indent=2)

    prompt = build_prompt(
        prompt_template,
        curriculum_json=curriculum_json,
        target_node_json=node_json,
        optional_context=optional_context,
        lesson_length_minutes=12,
    )
    print("template length:", len(prompt_template))
    print("curriculum JSON length:", len(curriculum_json))
    print("node JSON length:", len(node_json))
    print("lesson prompt length:", len(prompt))
    print("lesson prompt preview:", repr(prompt[:500]))

    content = invoke_gateway(
        model=model,
        prompt=prompt,
    )

    return Lesson.model_validate_json(content)



def generate_paginated_lesson(
    model: str,
    curriculum: Curriculum,
    node: CurriculumNode,
    optional_context: str = "",
    detail_level: DetailLevel = "standard",
) -> PaginatedLesson:
    if node.children:
        raise ValueError("Lesson generation requires a leaf node.")

    shared = load_prompt(PROMPT_DIR, SHARED_PROMPT_FILE)
    page1 = load_prompt(PROMPT_DIR, PAGE1_PROMPT_FILE)
    prompt_template = compose_prompts(shared, page1)

    curriculum_json = curriculum.model_dump_json(indent=2)
    node_json = node.model_dump_json(indent=2)

    prompt = build_prompt(
        prompt_template,
        topic=curriculum.title,
        curriculum_json=curriculum_json,
        target_node_json=node_json,
        optional_context=optional_context,
        detail_level=detail_level,
    )

    content_page1 = invoke_gateway(
        model=model,
        prompt=prompt,
    )
    start = LessonStart.model_validate_json(content_page1)

    expected_pages = EXPECTED_TOTAL_PAGES[detail_level]
    if start.total_pages not in expected_pages:
        raise ValueError(
            f"Expected total_pages in {expected_pages} for "
            f"detail_level={detail_level!r}, got {start.total_pages}"
        )
    lesson = PaginatedLesson(
        node_id=start.node_id,
        title=start.title,
        objective=start.objective,
        estimated_minutes=start.estimated_minutes,
        total_pages=start.total_pages,
        plan=start.plan,
        pages=[start.page],
        page_summaries=[start.page_summary],
        key_takeaways=start.key_takeaways if start.total_pages == 1 else [],
    )

    continuation = load_prompt(PROMPT_DIR, CONTINUATION_PROMPT_FILE)
    prompt_template = compose_prompts(shared, continuation)

    lesson_plan_json = json.dumps(
        [page.model_dump() for page in start.plan],
        indent=2,
    )

    for current_page in range(2, start.total_pages + 1):
        prior_page_summaries_json = json.dumps(
        lesson.page_summaries,
        indent=2,
    )

        prompt = build_prompt(
            prompt_template,
            target_node_json=node_json,
            optional_context=optional_context,
            current_page=current_page,
            total_pages=start.total_pages,
            lesson_plan_json=lesson_plan_json,
            prior_page_summaries_json=prior_page_summaries_json,
            detail_level=detail_level,
        )
        
        content = invoke_gateway(
                model=model,
                prompt=prompt,
            )
        continuation_result = LessonContinuation.model_validate_json(content)

        lesson.pages.append(continuation_result.page)
        lesson.page_summaries.append(continuation_result.page_summary)

        if current_page == start.total_pages:
            lesson.key_takeaways = continuation_result.key_takeaways

    return lesson