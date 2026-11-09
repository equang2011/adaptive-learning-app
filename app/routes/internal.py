import json
import os
import time
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.db.models import CurriculumRow, LessonRow
from app.db.session import DbSession
from app.models.curriculum import Curriculum
from app.services.curriculum import PROMPT_FILE as CURRICULUM_PROMPT_VERSION
from app.services.curriculum import find_node_by_id, generate_curriculum
from app.services.lesson import LESSON_PROMPT_VERSION, generate_paginated_lesson
from app.services.rate_limit import check_and_increment
from utils.markdown_render import render_markdown

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "app" / "templates"


templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters["markdown"] = render_markdown

CONFIG_DIR = ROOT / "app" / "config"
SCENARIO_FILE = CONFIG_DIR / "curriculum_scenarios.json"

MODEL = os.getenv("LESSON_MODEL", "deepseek-v4.1-flash-1017")

MAX_TOPIC_LENGTH = 200
MAX_CONTEXT_LENGTH = 2000

ALLOWED_DETAIL_LEVELS = {"quick", "standard", "deep"}


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


@router.get("/internal/curricula")
def list_curricula(request: Request, db: DbSession):
    # TODO (me): query CurriculumRow, newest first (created_at desc).
    # Return a list of rows (id, topic, model, created_at) plus a lesson
    # count per curriculum, e.g. a list of (CurriculumRow, lesson_count).
    curricula = []

    return templates.TemplateResponse(
        request=request,
        name="curricula_list.html",
        context={"curricula": curricula},
    )


@router.get("/internal/curricula/{curriculum_id}")
def curriculum_detail(request: Request, curriculum_id: int, db: DbSession):
    # TODO (me): load the CurriculumRow with id == curriculum_id, or None.
    # If it doesn't exist, raise HTTPException(404, "Curriculum not found").
    curriculum_row = None

    # TODO (me): query LessonRow where curriculum_id == curriculum_id,
    # newest first. Return a list of rows (id, node_id, detail_level, model,
    # created_at) for the lessons already generated for this curriculum.
    lessons = []

    return templates.TemplateResponse(
        request=request,
        name="curricula_detail.html",
        context={
            "curriculum_row": curriculum_row,
            "curriculum_id": curriculum_id,
            "lessons": lessons,
        },
    )


@router.post("/internal/curriculum")
def create_curriculum(
    request: Request,
    db: DbSession,
    topic: str = Form(...),
    optional_context: str = Form(""),
):
    validate_length(topic, "topic", MAX_TOPIC_LENGTH)
    validate_length(optional_context, "optional_context", MAX_CONTEXT_LENGTH)
    check_and_increment()

    start = time.perf_counter()
    curriculum = generate_curriculum(
        topic=topic,
        model=MODEL,
        optional_context=optional_context,
    )
    latency_ms = (time.perf_counter() - start) * 1000

    row = CurriculumRow(
        topic=topic,
        optional_context=optional_context or None,
        model=MODEL,
        prompt_version=CURRICULUM_PROMPT_VERSION,
        generation_latency_ms=latency_ms,
        content=curriculum.model_dump(mode="json"),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return templates.TemplateResponse(
        request=request,
        name="curriculum.html",
        context={
            "curriculum": curriculum,
            "curriculum_id": row.id,
            "lesson": None,
        },
    )


@router.post("/internal/lesson")
def create_lesson(
    request: Request,
    db: DbSession,
    curriculum_id: int = Form(...),
    node_id: str = Form(...),
    detail_level: str = Form("standard"),
):
    validate_detail_level(detail_level)

    curriculum_row = db.get(CurriculumRow, curriculum_id)
    if curriculum_row is None:
        raise HTTPException(
            status_code=404, detail=f"Curriculum not found: {curriculum_id}"
        )

    curriculum = Curriculum.model_validate(curriculum_row.content)
    db.rollback()

    target_node = None

    for node in curriculum.nodes:
        target_node = find_node_by_id(node, node_id)
        if target_node is not None:
            break
    if target_node is None:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    check_and_increment()

    start = time.perf_counter()
    lesson = generate_paginated_lesson(
        model=MODEL,
        curriculum=curriculum,
        node=target_node,
        detail_level=detail_level,
    )
    latency_ms = (time.perf_counter() - start) * 1000

    lesson_row = LessonRow(
        curriculum_id=curriculum_id,
        node_id=node_id,
        detail_level=detail_level,
        model=MODEL,
        prompt_version=LESSON_PROMPT_VERSION,
        generation_latency_ms=latency_ms,
        content=lesson.model_dump(mode="json"),
    )

    db.add(lesson_row)
    db.commit()
    db.refresh(lesson_row)

    return templates.TemplateResponse(
        request=request,
        name="curriculum.html",
        context={
            "curriculum": curriculum,
            "curriculum_id": curriculum_id,
            "lesson": lesson,
            "lesson_id": lesson_row.id,
            "selected_node_id": node_id,
        },
    )
