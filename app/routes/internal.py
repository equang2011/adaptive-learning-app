import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.models.curriculum import Curriculum, CurriculumNode
from app.models.lesson import PaginatedLesson
from app.services.curriculum import find_node_by_id, generate_curriculum
from app.services.jobs import DONE, get_job, start_job
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
LESSON_DATA_DIR = DATA_DIR / "lessons"

MODEL = os.getenv("LESSON_MODEL", "openai-gpt-6-luna")

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


def resolve_generation_path(filename: str, directory: Path | None = None) -> Path:
    """Resolve a user-supplied filename inside `directory` (default DATA_DIR),
    rejecting traversal."""
    if directory is None:
        directory = DATA_DIR

    if filename != Path(filename).name:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    candidate = (directory / filename).resolve()

    if candidate.parent != directory.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename.")

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    return candidate


def load_curriculum(filename: str) -> Curriculum:
    path = resolve_generation_path(filename)
    return Curriculum.model_validate_json(path.read_text(encoding="utf-8"))


def redirect_to_job(job_id: str) -> RedirectResponse:
    # 303 makes the browser follow up with a GET, so refreshing the job page
    # never re-submits the form.
    return RedirectResponse(f"/internal/jobs/{job_id}", status_code=303)


JOB_MESSAGES = {
    "curriculum": "Generating your curriculum, usually 30–60 seconds",
    "lesson": "Generating your lesson, usually 30–60 seconds",
}


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
    topic: str = Form(...),
    optional_context: str = Form(""),
):
    # Validation and the rate limit run now, so bad input fails immediately
    # instead of inside the background job.
    validate_length(topic, "topic", MAX_TOPIC_LENGTH)
    validate_length(optional_context, "optional_context", MAX_CONTEXT_LENGTH)
    check_and_increment()

    def work() -> str:
        curriculum = generate_curriculum(
            topic=topic,
            model=MODEL,
            optional_context=optional_context,
        )
        saved_path = save_curriculum(curriculum=curriculum, topic=topic, model=MODEL)
        return f"/internal/curriculum/{saved_path.name}"

    job = start_job("curriculum", work)
    return redirect_to_job(job.id)


@router.get("/internal/curriculum/{curriculum_filename}")
def view_curriculum(
    request: Request,
    curriculum_filename: str,
    lesson: str | None = None,
    node: str | None = None,
):
    curriculum = load_curriculum(curriculum_filename)

    context = {
        "curriculum": curriculum,
        "curriculum_filename": curriculum_filename,
        "lesson": None,
    }

    if lesson is not None:
        lesson_path = resolve_generation_path(lesson, LESSON_DATA_DIR)
        context["lesson"] = PaginatedLesson.model_validate_json(
            lesson_path.read_text(encoding="utf-8")
        )
        context["lesson_filename"] = lesson
    if node is not None:
        context["selected_node_id"] = node

    return templates.TemplateResponse(
        request=request,
        name="curriculum.html",
        context=context,
    )


@router.post("/internal/lesson")
def create_lesson(
    curriculum_filename: str = Form(...),
    node_id: str = Form(...),
    detail_level: str = Form("standard"),
):
    validate_detail_level(detail_level)
    curriculum = load_curriculum(curriculum_filename)

    target_node = None

    for node in curriculum.nodes:
        target_node = find_node_by_id(node, node_id)
        if target_node is not None:
            break
    if target_node is None:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    check_and_increment()

    def work() -> str:
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
        query = urlencode({"lesson": saved_path.name, "node": node_id})
        return f"/internal/curriculum/{curriculum_filename}?{query}"

    job = start_job("lesson", work)
    return redirect_to_job(job.id)


@router.get("/internal/jobs/{job_id}")
def view_job(request: Request, job_id: str):
    job = get_job(job_id)

    # Already finished (e.g. the user came back after switching apps):
    # skip the waiting page and go straight to the result.
    if job is not None and job.status == DONE:
        return RedirectResponse(job.result_url, status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="job.html",
        context={
            "job": job,
            "message": JOB_MESSAGES.get(job.kind, "Working…") if job else None,
            # Sent as "seconds so far" rather than a timestamp, so the timer is
            # right even if the phone's clock disagrees with the server's.
            "elapsed_seconds": int(time.time() - job.started_at) if job else 0,
        },
        status_code=200 if job else 404,
    )


@router.get("/internal/jobs/{job_id}/status")
def job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        return JSONResponse({"status": "missing"}, status_code=404)

    return {
        "status": job.status,
        "result_url": job.result_url,
        "error": job.error,
    }
