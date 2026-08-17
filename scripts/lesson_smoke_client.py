from datetime import datetime
from pathlib import Path

from app.models.curriculum import Curriculum, CurriculumNode
from app.models.lesson import PaginatedLesson
from app.services.lesson import generate_paginated_lesson

MODEL = "openai/gpt-5.6-luna"

ROOT = Path(__file__).resolve().parents[1]

CURRICULUM_DIR = ROOT / "data" / "generations"
LESSON_DIR = ROOT / "data" / "lessons"

CURRICULUM_FILE = CURRICULUM_DIR / "backend_fundamentals_002.json"

TARGET_NODE_ID = "logging"


def find_node_by_id(
    node: CurriculumNode,
    node_id: str,
) -> CurriculumNode | None:

    if node.id == node_id:
        return node

    for child in node.children:
        result = find_node_by_id(child, node_id)

        if result is not None:
            return result

    return None


def save_lesson(
    lesson: PaginatedLesson,
    node: CurriculumNode,
    model: str,
) -> Path:
    LESSON_DIR.mkdir(parents=True, exist_ok=True)

    model_slug = model.replace("/", "_")[:20]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lesson_{node.id}_v1_{model_slug}_{timestamp}.json"

    output_path = LESSON_DIR / filename
    json_lesson = lesson.model_dump_json(indent=2)

    output_path.write_text(json_lesson, encoding="utf-8")

    return output_path


def main():
    curriculum_string = CURRICULUM_FILE.read_text(encoding="utf-8")

    curriculum = Curriculum.model_validate_json(curriculum_string)

    target_node = None

    for node in curriculum.nodes:
        target_node = find_node_by_id(node, TARGET_NODE_ID)
        if target_node is not None:
            break
    if target_node is None:
        raise ValueError(f"Node not found: {TARGET_NODE_ID}")

    print(target_node)

    lesson = generate_paginated_lesson(
        model=MODEL,
        curriculum=curriculum,
        node=target_node,
    )
    print(lesson.model_dump_json(indent=2))

    saved_path = save_lesson(lesson=lesson, node=target_node, model=MODEL)
    print("saved:", saved_path)


if __name__ == "__main__":
    main()
