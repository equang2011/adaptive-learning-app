from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class LessonSection(BaseModel):
    heading: str
    content: str


class Lesson(BaseModel):
    node_id: str
    title: str
    objective: str
    estimated_minutes: int
    introduction: str
    sections: list[LessonSection]
    example: str
    key_takeaways: list[str]


class LessonGenerationRecord(BaseModel):
    id: UUID
    model: str
    prompt_version: str
    curriculum_filename: str
    created_at: datetime
    generation_latency_ms: float
    validation_status: Literal["not_attempted", "passed", "failed"]
    lesson: Lesson | None

DetailLevel = Literal["quick", "standard", "deep"]


class LessonPagePlan(BaseModel):
    page_number: int
    title: str
    objective: str
    estimated_minutes: int


class LessonPage(BaseModel):
    page_number: int
    title: str
    introduction: str
    sections: list[LessonSection]
    example: str


class LessonStart(BaseModel):
    node_id: str
    title: str
    objective: str
    estimated_minutes: int
    total_pages: int
    plan: list[LessonPagePlan]
    page: LessonPage
    page_summary: str
    key_takeaways: list[str] = Field(default_factory=list)


class LessonContinuation(BaseModel):
    node_id: str
    page: LessonPage
    page_summary: str
    key_takeaways: list[str]


class PaginatedLesson(BaseModel):
    node_id: str
    title: str
    objective: str
    estimated_minutes: int
    total_pages: int
    plan: list[LessonPagePlan]
    pages: list[LessonPage]
    page_summaries: list[str]
    key_takeaways: list[str] = Field(default_factory=list)

