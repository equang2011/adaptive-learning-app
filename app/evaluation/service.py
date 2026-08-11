import os
from pathlib import Path

from app.clients.gateway import invoke_gateway
from app.evaluation.models import LessonEvaluation
from app.models.curriculum import CurriculumNode
from app.models.lesson import Lesson
from utils.prompt_builder import build_prompt, load_prompt

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts"
LESSON_EVALUATOR_PROMPT_FILE = os.getenv("LESSON_EVALUATOR_PROMPT_VERSION", "lesson_evaluator_v1.md")
CURRICULUM_EVALUATOR_PROMPT_FILE = os.getenv("CURRICULUM_EVALUATOR_PROMPT_VERSION", "curriculum_evaluator_v1.md")


def evaluate_lesson(
    model: str,
    lesson: Lesson,
    node: CurriculumNode,
) -> LessonEvaluation:


    prompt_template = load_prompt(
        PROMPT_DIR,
        LESSON_EVALUATOR_PROMPT_FILE
    )

    lesson_json = lesson.model_dump_json(indent=2)
    node_json = node.model_dump_json(indent=2)

    prompt = build_prompt(
        prompt_template,
        lesson_json=lesson_json,
        target_node_json=node.json,
    )

    content = invoke_gateway(
        model=model,
        prompt=prompt,
    )

    return LessonEvaluation.model_validate_json(content)
