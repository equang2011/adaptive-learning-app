import json
from datetime import datetime
from pathlib import Path

from app.services.curriculum import generate_curriculum


ROOT = Path(__file__).resolve().parents[3]
CURRICULUM_INPUTS = ROOT / "data" / "test_inputs" / "curriculum_test_cases_1.json"
MODEL = "deepseek/deepseek-v4-flash-0731"

GENERATIONS_DIR = ROOT / "data" / "generations"


def find_latest_run_dir() -> Path | None:
    batches = sorted(GENERATIONS_DIR.glob("batch_*"))
    return batches[-1] if batches else None


def load_summary(run_dir: Path) -> list[dict]:
    summary_path = run_dir / "_summary.json"
    if summary_path.exists():
        return json.loads(summary_path.read_text(encoding="utf-8"))
    return []


def write_summary(run_dir: Path, summary: list[dict]) -> None:
    summary_path = run_dir / "_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main():
    existing_run = find_latest_run_dir()

    if existing_run is not None:
        run_dir = existing_run
        summary = load_summary(run_dir)
        print(f"Resuming run: {run_dir.name}")
    else:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
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

        try:
            curriculum = generate_curriculum(
                topic=test_case["topic"],
                optional_context=test_case["optional_context"],
                model=MODEL,
            )
        except Exception as err:
            print(f"[{scenario_id}] FAILED: {err}")
            summary.append({"scenario_id": scenario_id, "status": "failed", "error": str(err)})
            write_summary(run_dir, summary)
            continue

        record = {
            "scenario_id": scenario_id,
            "topic": test_case["topic"],
            "optional_context": test_case["optional_context"],
            "model": MODEL,
            "curriculum": curriculum.model_dump(),
        }

        output_path = run_dir / f"{scenario_id}.json"
        output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

        print(f"[{scenario_id}] saved: {output_path.name}")
        summary.append({"scenario_id": scenario_id, "status": "success", "file": output_path.name})
        write_summary(run_dir, summary)

    print(f"\nRun complete: {run_dir}")


if __name__ == "__main__":
    main()