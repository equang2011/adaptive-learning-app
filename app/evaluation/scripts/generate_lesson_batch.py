import json
import os
from datetime import datetime, timezone
from pathlib import Path


from app.models.curriculum import Curriculum
from app.services.curriculum import find_node_by_id
from app.services.lesson import generate_paginated_lesson

MODEL = os.getenv(
    "LESSON_MODEL",
    "openai/gpt-5.6-luna",
)
DETAIL_LEVEL = os.getenv("LESSON_DETAIL_LEVEL", "standard")

ROOT = Path(__file__).resolve().parents[3]

CURRICULUM_DIR = ROOT/ "data" / "generations" /"batch_20260815_231554"
MANIFEST_FILE_PATH = ROOT / "data" / "test_inputs" / "lesson_test_cases_1.json"


def main():
    batch_id = datetime.now().strftime("%Y%m%d_%H00")
    batch_name = f"batch_{batch_id}"

    output_dir = ROOT / "data" / "lessons" / batch_name
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(
        MANIFEST_FILE_PATH.read_text(encoding="utf-8")
    )

    generated_count = 0
    for test_case in manifest:
        scenario_id = test_case["id"]
        curriculum_file = test_case["curriculum_file"]
        curriculum_path = CURRICULUM_DIR / curriculum_file

        print(f"\n[{scenario_id}] loading curriculum...")
        print(f"[{scenario_id}] model: {MODEL}")
        curriculum_record = json.loads(
            curriculum_path.read_text(encoding="utf-8")
        )

        curriculum = Curriculum.model_validate(
            curriculum_record["curriculum"]
        )

        # Find the right node
        target_node_id = test_case["target_node_id"]
        target_node = None

        for node in curriculum.nodes:
            target_node = find_node_by_id(node, target_node_id)
            if target_node is not None:
                break

        if target_node is None:
            raise ValueError(f"Node not found: {target_node_id}")

        print(
            f"[{scenario_id}] generating lesson for "
            f"{target_node.title}..."
        )

        lesson = generate_paginated_lesson(
            model=MODEL,
            curriculum=curriculum,
            node=target_node,
            optional_context=curriculum_record.get("optional_context", ""),
            detail_level=DETAIL_LEVEL,
        )

        print(
            f"[{scenario_id}] lesson generated successfully "
            f"({lesson.total_pages} pages)"
        )

        output_path = output_dir / f"{scenario_id}.json"

        output_path.write_text(
            lesson.model_dump_json(indent=2),
            encoding="utf-8",
        )
        generated_count += 1

        print(f"[{scenario_id}] saved to {output_path.name}")
        print(f"[{scenario_id}] saved in folder: {output_path}")
    print(f"\nBatch complete: {output_dir}")
    print(f"Lessons generated and saved: {generated_count}/{len(manifest)}")

if __name__ == "__main__":
    main()