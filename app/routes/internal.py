import json
import os
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.models.curriculum import Curriculum, CurriculumNode
from app.models.lesson import PaginatedLesson
from app.services.curriculum import find_node_by_id, generate_curriculum
from app.services.lesson import generate_paginated_lesson
from app.services.rate_limit import check_and_increment
from utils.markdown_render import render_markdown

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "app" / "templates"


templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters["markdown"] = render_markdown

CONFIG_DIR = ROOT / "app" / "config"
SCENARIO_FILE = CONFIG_DIR / "curriculum_scenarios.json"

DATA_DIR = ROOT / "data" / "generations"

MODEL = os.getenv("LESSON_MODEL", "openai/gpt-6-luna")

MAX_TOPIC_LENGTH = 200
MAX_CONTEXT_LENGTH = 2000

ALLOWED_DETAIL_LEVELS = {"quick", "standard", "deep"}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def save_curriculum(
    curriculum: Curriculum,
    topic: str,
    model: str,
) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    topic_slug = slugify(topic)[:40]
    model_slug = slugify(model)[:30]

    filename = f"curriculum_{topic_slug}_{model_slug}_{timestamp}.json"

    output_path = DATA_DIR / filename

    output_path.write_text(
        curriculum.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return output_path

def save_lesson(
    lesson: PaginatedLesson,
    node: CurriculumNode,
    model: str,
    curriculum_file_name: str,
) -> Path:
    prompt_version = os.getenv('LESSON_PROMPT_VERSION', None)
    
    LESSON_DATA_DIR = DATA_DIR / "lessons"
    LESSON_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title_slug = slugify(lesson.title[:35])
    model_slug = slugify(model)[:30]
    filename = f"lesson_{title_slug}_{model_slug}_{timestamp}.json"

    output_path = LESSON_DATA_DIR / filename
    output_path.write_text(
            lesson.model_dump_json(indent=2),
            encoding="utf-8",
        )
    return output_path

def validate_detail_level(detail_level: str) -> None:
    if detail_level not in ALLOWED_DETAIL_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown detail_level: {detail_level!r}",
        )


def validate_length(value: str, field: str, maximum: int) -> None:
    if len(value) > maximum:
        raise HTTPException(
            status_code=400,
            detail=f"{field} exceeds maximum length of {maximum} characters.",
        )


def resolve_generation_path(filename: str) -> Path:
    """Resolve a user-supplied filename inside DATA_DIR, rejecting traversal."""
    if filename != Path(filename).name:
        raise HTTPException(status_code=400, detail="Invalid curriculum filename.")

    candidate = (DATA_DIR / filename).resolve()

    if candidate.parent != DATA_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid curriculum filename.")

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Curriculum not found.")

    return candidate


@router.get("/internal")
def internal_home(request: Request):
    scenario_json = SCENARIO_FILE.read_text(encoding="utf-8")
    scenarios = json.loads(scenario_json)
    return templates.TemplateResponse(
        request=request,
        name="internal_home.html",
        context={
            "scenarios": scenarios,
        },
    )


@router.post("/internal/curriculum")
def create_curriculum(
    request: Request,
    topic: str = Form(...),
    optional_context: str = Form(""),
):
    validate_length(topic, "topic", MAX_TOPIC_LENGTH)
    validate_length(optional_context, "optional_context", MAX_CONTEXT_LENGTH)
    check_and_increment()

    curriculum = generate_curriculum(
        topic=topic,
        model=MODEL,
        optional_context=optional_context,
    )

    saved_path = save_curriculum(curriculum=curriculum, topic=topic, model=MODEL)

    return templates.TemplateResponse(
        request=request,
        name="curriculum.html",
        context={
            "curriculum": curriculum,
            "curriculum_filename": saved_path.name,
            "lesson": None,
        },
    )


@router.post("/internal/lesson")
def create_lesson(
    request: Request,
    curriculum_filename: str = Form(...),
    node_id: str = Form(...),
    detail_level: str = Form("standard"),
):
    validate_detail_level(detail_level)
    curriculum_path = resolve_generation_path(curriculum_filename)

    curriculum_string = curriculum_path.read_text(encoding="utf-8")
    curriculum = Curriculum.model_validate_json(curriculum_string)

    target_node = None

    for node in curriculum.nodes:
        target_node = find_node_by_id(node, node_id)
        if target_node is not None:
            break
    if target_node is None:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    check_and_increment()

    lesson = generate_paginated_lesson(
        model=MODEL,
        curriculum=curriculum,
        node=target_node,
        detail_level=detail_level,
    )

    saved_path = save_lesson(
        lesson=lesson,
        node=target_node,
        model=MODEL,
        curriculum_file_name=curriculum_filename,
    )

    return templates.TemplateResponse(
        request=request,
        name="curriculum.html",
        context={
            "curriculum": curriculum,
            "curriculum_filename": curriculum_filename,
            "lesson": lesson,
            "lesson_filename": saved_path.name,
            "selected_node_id": node_id,
        },
    )
