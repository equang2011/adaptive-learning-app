from typing import Literal

from pydantic import BaseModel, Field


class LessonEvaluationIssue(BaseModel):
    category: str
    description: str
    severity: Literal["low", "medium", "high"]


class CurriculumEvaluationIssue(BaseModel):
    category: Literal[
        "coverage",
        "sequencing",
        "leaf_granularity",
        "redundancy",
        "learner_context_fit",
        "structural_coherence",
        "other",
    ]
    severity: Literal["low", "medium", "high"]
    description: str


class LessonEvaluation(BaseModel):
    scope_adherence: int = Field(ge=1, le=5)
    factual_consistency: int = Field(ge=1, le=5)
    pedagogical_clarity: int = Field(ge=1, le=5)
    internal_consistency: int = Field(ge=1, le=5)
    lesson_granularity: int = Field(ge=1, le=5)

    overall_score: float = Field(ge=1, le=5)

    issues: list[LessonEvaluationIssue]
    summary: str


class CurriculumEvaluation(BaseModel):
    coverage: int = Field(ge=1, le=5)
    sequencing: int = Field(ge=1, le=5)
    leaf_granularity: int = Field(ge=1, le=5)
    redundancy: int = Field(ge=1, le=5)
    learner_context_fit: int = Field(ge=1, le=5)
    structural_coherence: int = Field(ge=1, le=5)
    overall_score: float = Field(ge=1, le=5)
    strengths: list[str]
    issues: list[CurriculumEvaluationIssue]
    summary: str
