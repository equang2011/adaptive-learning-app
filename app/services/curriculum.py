from pathlib import Path

from app.models.curriculum import Curriculum

from app.clients.gateway import invoke_gateway
from utils.prompt_builder import load_prompt, build_prompt

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts"
PROMPT_FILE = 'curriculum_v4.md'

def generate_curriculum(
    topic: str,
    model: str,
    optional_context: str = "",
) -> Curriculum:
    prompt_template = load_prompt(PROMPT_DIR, PROMPT_FILE)

    prompt = build_prompt(
        prompt_template,
        topic=topic,
        optional_context=optional_context,
    )

    content = invoke_gateway(
        model=model,
        prompt=prompt,
    )

    return Curriculum.model_validate_json(content)

