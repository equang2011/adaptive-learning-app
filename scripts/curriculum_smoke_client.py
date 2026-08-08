from datetime import datetime
from pathlib import Path

from app.models.curriculum import Curriculum, CurriculumNode
from app.services.curriculum import generate_curriculum

TOPIC = """
Teach me the fundamentals of distributed systems. I know Python and basic backend development, but I have very little experience with networking or distributed infrastructure.
"""

MODEL = 'deepseek/deepseek-v4-flash-0731'

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "generations"


def count_leaves(node: CurriculumNode) -> int:
    if not node.children:
        return 1

    cnt = 0
    for child in node.children:
        cnt += count_leaves(child)

    return cnt


def save_curriculum(curriculum: Curriculum,) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"curriculum_{timestamp}.json"
    output_path = DATA_DIR / filename
    json_curriculum = curriculum.model_dump_json(indent=2)

    output_path.write_text(
        json_curriculum,
        encoding="utf-8"
    )

    return output_path


def main():
    curriculum = generate_curriculum(
        topic=TOPIC,
        model=MODEL,
    )

    print(curriculum.title)
    print("modules:", len(curriculum.nodes))
    print(
        "leaves:",
        sum(count_leaves(node) for node in curriculum.nodes),
    )

    saved_path= save_curriculum(curriculum=curriculum)
    print("saved:", saved_path)


if __name__ == "__main__":
    main()
