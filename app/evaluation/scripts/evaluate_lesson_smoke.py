
from pathlib import Path

from app.evaluation.service import evaluate_lesson
from app.models.curriculum import Curriculum, CurriculumNode
from app.models.lesson import Lesson

"""

target a single lesson

"""
ROOT = Path(__file__).resolve().parents[3]
LESSON_FILE = ROOT / "data" / "lessons" / "lesson_m4-s1-l3_v1_tencent_hy3_20260808_200933.json"
CURRICULUM_FILE = ROOT / "data" / "generations" / "curriculum_20260808_183819.json"

MODEL = "deepseek/deepseek-v4-flash-0731"


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

def main():
    lesson = Lesson.model_validate_json(LESSON_FILE.read_text(encoding="utf-8"))
    curriculum = Curriculum.model_validate_json(CURRICULUM_FILE.read_text(encoding="utf-8"))

    node = None
    for top_level_node in curriculum.nodes:
        node = find_node_by_id(top_level_node, lesson.node_id)
        if node is not None:
            break
    if node is None:
        raise ValueError(f"Node not found: {lesson.node_id}")

    evaluation = evaluate_lesson(model=MODEL, lesson=lesson, node=node)

    print(evaluation.model_dump_json(indent=2))

if __name__ == "__main__":
    main()



