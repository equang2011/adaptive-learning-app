from pydantic import BaseModel


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
