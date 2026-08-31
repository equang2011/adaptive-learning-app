import json
from pathlib import Path

from app.evaluation.scripts.batch_utils import (
    find_latest_run_dir,
    load_summary,
    write_summary,
)
from app.evaluation.service import evaluate_curriculum
from app.models.curriculum import Curriculum

ROOT = Path(__file__).resolve().parents[3]
MODEL = "deepseek/deepseek-v4-flash-0731"
GENERATIONS_DIR = ROOT / "data" / "generations"
EVALUATIONS_DIR = ROOT / "data" / "evaluations"
MAX_ATTEMPTS = 3


def main():
    source_run = find_latest_run_dir(GENERATIONS_DIR)
    eval_run_dir = EVALUATIONS_DIR / source_run.name
    eval_run_dir.mkdir(parents=True, exist_ok=True)

    summary = load_summary(eval_run_dir)
    completed_ids = {entry["scenario_id"] for entry in summary if entry["status"] == "success"}

    limit = 10
    cnt = 0

    for file_path in sorted(source_run.glob("*.json")):
        if file_path.name == "_summary.json":
            continue
        if cnt >= limit:
            break

        record = json.loads(file_path.read_text(encoding="utf-8"))
        scenario_id = record["scenario_id"]

        if scenario_id in completed_ids:
            print(f"[{scenario_id}] already evaluated, skipping")
            continue

        cnt += 1
        curriculum = Curriculum.model_validate(record["curriculum"])

        evaluation = None
        last_err = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                evaluation = evaluate_curriculum(
                    model=MODEL,
                    curriculum=curriculum,
                    topic=record["topic"],
                    optional_context=record["optional_context"],
                )
                break
            except Exception as err:
                last_err = err
                print(f"[{scenario_id}] attempt {attempt}/{MAX_ATTEMPTS} failed: {err}")

        if evaluation is None:
            print(f"[{scenario_id}] FAILED after {MAX_ATTEMPTS} attempts: {last_err}")
            summary.append({"scenario_id": scenario_id, "status": "failed", "error": str(last_err)})
            write_summary(eval_run_dir, summary)
            continue

        output_path = eval_run_dir / f"{scenario_id}.json"
        output_path.write_text(evaluation.model_dump_json(indent=2), encoding="utf-8")

        print(f"[{scenario_id}] saved: {output_path.name}")

        summary.append({"scenario_id": scenario_id, "status": "success", "file": output_path.name})
        write_summary(eval_run_dir, summary)


    print(f"\nCurriculum evaluation complete: {eval_run_dir}")


if __name__ == "__main__":
    main()
