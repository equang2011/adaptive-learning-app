
from pathlib import Path


def load_prompt(path: Path, filename: str) -> str:
    prompt_path = path / filename
    return prompt_path.read_text(encoding="utf-8")


def build_prompt(template: str, topic: str, optional_context: str = "") -> str:


    return template.format(
        topic=topic,
        optional_context=optional_context,
    )
