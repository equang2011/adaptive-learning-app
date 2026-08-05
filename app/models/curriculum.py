from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CurriculumNode(BaseModel):
    id: str
    title: str
    objective: str
    children: list["CurriculumNode"] = Field(default_factory=list)


class Curriculum(BaseModel):
    title: str
    description: str
    nodes: list[CurriculumNode]


class CurriculumGenerationRecord(BaseModel):
    id: UUID
    topic: str
    model: str
    prompt_version: str
    created_at: datetime
    generation_latency_ms: float
    validation_status: Literal["not_attempted", "passed", "failed"]
    retry_count: int
    raw_model_output: str
    curriculum: Curriculum | None
