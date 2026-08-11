from app.models.claims import ClaimExtraction
from app.models.lesson import Lesson


def extract_material_claims(
    model: str,
    lesson: Lesson,
) -> ClaimExtraction:

    # load claim_extractor_v1.md
    # lesson.model_dump_json(indent=2)
    # build_prompt(...)
    # invoke_gateway(...)
    # ClaimExtraction.model_validate_json(...)
    pass
