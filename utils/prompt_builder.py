from pathlib import Path


def load_prompt(path: Path, filename: str) -> str:
    prompt_path = path / filename
    return prompt_path.read_text(encoding="utf-8")


def build_prompt(template: str, **values: object) -> str:
    return template.format(**values)
