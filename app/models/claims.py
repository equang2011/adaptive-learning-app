from typing import Literal

from pydantic import BaseModel, Field


class MaterialClaim(BaseModel):
    id: str

    source_field: str
    claim_text: str

    claim_type: Literal[
        "legal_regulatory",
        "quantitative",
        "technical",
        "scientific",
        "historical",
        "temporal",
        "other",
    ]

    materiality: int = Field(ge=1, le=5)
    verification_priority: int = Field(ge=1, le=5)

    reason_to_verify: str


class ClaimExtraction(BaseModel):
    claims: list[MaterialClaim]
