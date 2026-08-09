import json, re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.models.curriculum import Curriculum, CurriculumNode
from app.services.curriculum import generate_curriculum
from app.services.lesson import generate_lesson

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "app" / "templates"


templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

SCENARIO_FILE = ROOT / "data" / "test_inputs" / "curriculum_scenarios.json"
MODEL_FILE = ROOT / "data" / "test_inputs" / "models.json"

DATA_DIR = ROOT / "data" / "generations"

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

    filename = (
        f"curriculum_{topic_slug}_{model_slug}_{timestamp}.json"
    )

    output_path = DATA_DIR / filename

    output_path.write_text(
        curriculum.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return output_path

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

def load_models() -> list[dict]:
    model_json = MODEL_FILE.read_text(encoding="utf-8")
    return json.loads(model_json)

@router.get("/internal")
def internal_home(request: Request):
    scenario_json = SCENARIO_FILE.read_text(encoding="utf-8")
    scenarios = json.loads(scenario_json)
    model_json = MODEL_FILE.read_text(encoding="utf-8")
    models = json.loads(model_json)
    return templates.TemplateResponse(
        request=request,
        name="internal_home.html",
        context={"scenarios": scenarios,
                 "models":models,},
    )

@router.post("/internal/curriculum")
def create_curriculum(
    request: Request,
    topic: str = Form(...),
    optional_context: str = Form(""),
    model:str = Form(...),
):

    curriculum = generate_curriculum(
        topic=topic,
        model=model,
        optional_context=optional_context,
    )

    saved_path = save_curriculum(
        curriculum=curriculum,
        topic=topic,
        model=model
    )

    return templates.TemplateResponse(
        request=request,
        name="curriculum.html",
        context={
            "curriculum": curriculum,
            "curriculum_filename": saved_path.name,
            "models": load_models(),
            "lesson": None,
        },
    )



@router.post("/internal/lesson")
def create_lesson(
    request: Request,
    curriculum_filename: str = Form(...),
    node_id: str = Form(...),
    lesson_model: str = Form(...),
):
    curriculum_path = DATA_DIR / curriculum_filename

    curriculum_string = curriculum_path.read_text(
    encoding="utf-8"
    )
    curriculum = Curriculum.model_validate_json(curriculum_string)

    target_node = None
    
    for node in curriculum.nodes:
        target_node = find_node_by_id(node, node_id)
        if target_node is not None:
            break
    if target_node is None:
        raise ValueError(f"Node not found: {node_id}")

   
    lesson = generate_lesson(
        model=lesson_model,
        curriculum=curriculum,
        node=target_node,
    )

    return templates.TemplateResponse(
    request=request,
    name="curriculum.html",
    context={
        "curriculum": curriculum,
        "curriculum_filename": curriculum_filename,
        "models": load_models(),
        "lesson": lesson,
        "selected_node_id": node_id,
    },
)
    


    
