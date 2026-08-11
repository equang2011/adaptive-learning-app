import os
from pathlib import Path

from app.clients.gateway import invoke_gateway
from app.models.curriculum import Curriculum, CurriculumNode
from app.models.lesson import Lesson
from utils.prompt_builder import build_prompt, load_prompt

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts"
PROMPT_FILE = os.getenv("LESSON_PROMPT_VERSION", "lesson_v1.7.md")


def generate_lesson(
    model: str,
    curriculum: Curriculum,
    node: CurriculumNode,
    optional_context: str = "",
) -> Lesson:
    if node.children:
        raise ValueError("Lesson generation requires a leaf node.")
    prompt_template = load_prompt(PROMPT_DIR, PROMPT_FILE)
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
