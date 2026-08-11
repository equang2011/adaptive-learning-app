from app.models.curriculum import Curriculum
from app.models.evaluation import CurriculumEvaluation


def evaluate_curriculum(
    model: str,
    curriculum: Curriculum,
    topic: str,
    optional_context: str = "",
) -> CurriculumEvaluation:
    """
        load curriculum_evaluator_v1.md
            ↓
    curriculum.model_dump_json(indent=2)
            ↓
    build_prompt(
        topic=...,
        optional_context=...,
        curriculum_json=...,
    )
            ↓
    invoke_gateway(...)
            ↓
    CurriculumEvaluation.model_validate_json(...)
            ↓
    return evaluation
    """
