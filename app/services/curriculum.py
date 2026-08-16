import os
import random
from pathlib import Path

from app.clients.gateway import invoke_gateway
from app.models.curriculum import Curriculum, CurriculumNode
from utils.prompt_builder import build_prompt, load_prompt

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts"
PROMPT_FILE = os.getenv("CURRICULUM_PROMPT_VERSION", "curriculum_v4.md")


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
        lesson_length_minutes=10,
    )

    content = invoke_gateway(
        model=model,
        prompt=prompt,
    )

    return Curriculum.model_validate_json(content)


def find_node_by_id(
    node: CurriculumNode,
    node_id: str,
) -> CurriculumNode | None:

    if node.id == node_id:
        return node

    for child in node.children:
        result = find_node_by_id(child, node_id)

        if result is not None:
            return result

    return None


def get_leaf_nodes(nodes: list[CurriculumNode]) -> list[CurriculumNode]:
    leaves = []

    for node in nodes:
        if not node.children:
            leaves.append(node)
        else:
            leaves.extend(get_leaf_nodes(node.children))

    return leaves


def get_random_leaf(curriculum: Curriculum) -> CurriculumNode:
    leaves = get_leaf_nodes(curriculum.nodes)

    if not leaves:
        raise ValueError("Curriculum has no leaf nodes")

    return random.choice(leaves)
