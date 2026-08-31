import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.evaluation.scripts.batch_utils import (
    find_latest_run_dir,
    load_summary,
    write_summary,
)
from app.services.curriculum import generate_curriculum

ROOT = Path(__file__).resolve().parents[3]
CURRICULUM_INPUTS = ROOT / "data" / "test_inputs" / "curriculum_test_cases_1.json"
MODEL = "deepseek/deepseek-v4-flash-0731"

GENERATIONS_DIR = ROOT / "data" / "generations"


def main():
    existing_run = find_latest_run_dir(GENERATIONS_DIR)

    if existing_run is not None:
        run_dir = existing_run
        summary = load_summary(run_dir)
        print(f"Resuming run: {run_dir.name}")
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        run_dir = GENERATIONS_DIR / f"batch_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        summary = []
        print(f"Starting new run: {run_dir.name}")

    completed_ids = {entry["scenario_id"] for entry in summary if entry["status"] == "success"}

    with CURRICULUM_INPUTS.open("r", encoding="utf-8") as f:
        test_cases = json.load(f)

    for test_case in test_cases:
        scenario_id = test_case["id"]

        if scenario_id in completed_ids:
            print(f"[{scenario_id}] already succeeded, skipping")
            continue

        summary = [entry for entry in summary if entry["scenario_id"] != scenario_id]

        print(f"[{scenario_id}] generating...")

        start = time.perf_counter()
        try:
            curriculum = generate_curriculum(
                topic=test_case["topic"],
                optional_context=test_case["optional_context"],
                model=MODEL,
            )
        except Exception as err:
            elapsed = time.perf_counter() - start
            print(f"[{scenario_id}] FAILED: {err}")
            summary.append({"scenario_id": scenario_id, "status": "failed", "error": str(err), "elapsed_seconds": round(elapsed,1)})
            write_summary(run_dir, summary)
            continue

        elapsed = round(time.perf_counter() - start, 1)
        
        record = {
            "scenario_id": scenario_id,
            "topic": test_case["topic"],
            "optional_context": test_case["optional_context"],
            "model": MODEL,
            "elapsed_seconds": elapsed,
            "curriculum": curriculum.model_dump(),
        }

        output_path = run_dir / f"{scenario_id}.json"
        output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

        print(f"[{scenario_id}] saved: {output_path.name}")
        summary.append({"scenario_id": scenario_id, "status": "success", "file": output_path.name, "elapsed_seconds": elapsed})
        write_summary(run_dir, summary)

    print(f"\nRun complete: {run_dir}")


if __name__ == "__main__":
    main()