from pathlib import Path
import json


from app.evaluation.service import evaluate_curriculum
from app.models.curriculum import Curriculum


ROOT = Path(__file__).resolve().parents[3]
BATCH_FILE = ROOT / "data" / "generations" / "batch_20260815_231554" / "distributed_systems.json"
MODEL = "deepseek/deepseek-v4-flash-0731"


def main():
    record = json.loads(BATCH_FILE.read_text(encoding="utf-8"))
    curriculum = Curriculum.model_validate(record["curriculum"])

    evaluation = evaluate_curriculum(
        model=MODEL,
        curriculum=curriculum,
        topic=record["topic"],
        optional_context=record["optional_context"],
    )

    print(evaluation.model_dump_json(indent=2))

if __name__ == "__main__":
    main()