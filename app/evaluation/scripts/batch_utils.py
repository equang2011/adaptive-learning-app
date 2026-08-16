import json
from pathlib import Path


def find_latest_run_dir(parent_dir: Path) -> Path | None:
    batches = sorted(parent_dir.glob("batch_*"))
    return batches[-1] if batches else None


def load_summary(run_dir: Path) -> list[dict]:
    summary_path = run_dir / "_summary.json"
    if summary_path.exists():
        return json.loads(summary_path.read_text(encoding="utf-8"))
    return []


def write_summary(run_dir: Path, summary: list[dict]) -> None:
    summary_path = run_dir / "_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def combine_batch_files(run_dir: Path, output_filename: str = "_combined.json") -> Path:
    combined = []

    for file_path in sorted(run_dir.glob("*.json")):
        if file_path.name in {"_summary.json", output_filename}:
            continue

        content = json.loads(file_path.read_text(encoding="utf-8"))
        combined.append({"name": file_path.stem, **content})

    output_path = run_dir / output_filename
    output_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    return output_path
