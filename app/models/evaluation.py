from typing import Literal

from pydantic import BaseModel


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


class CurriculumEvaluation(BaseModel):
    # your turn:
    # six rubric scores, each constrained 1–5
    # overall_score, also 1–5
    # strengths: list[str]
    # issues: list[CurriculumEvaluationIssue]
    # summary: str
    pass
