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


# Future: multi-page lesson generation (lesson_v1.8 exploration)
#
# Motivation: generate a lesson plan first, then individual pages in separate
# requests. Allows user to browse/navigate the planned structure before
# rendering all content, and keeps per-request token budgets smaller.
#
# Proposed flow:
#   1. generate_lesson_plan() -> LessonGenerationStart (with plan only)
#   2. generate_lesson_page(node_id, page_number) -> LessonPage (one page)
#
# Model sketch:
#
#   class LessonPagePlan(BaseModel):
#       page_number: int
#       title: str
#       objective: str
#       estimated_minutes: int
#
#   class LessonPage(BaseModel):
#       page_number: int
#       title: str
#       introduction: str
#       sections: list[LessonSection]
#       example: str
#
#   class LessonGenerationStart(BaseModel):
#       node_id: str
#       title: str
#       objective: str
#       estimated_minutes: int
#       plan: list[LessonPagePlan]
#       page: LessonPage  # first page included with the plan
#
# Not implemented yet. See lesson_v1.8.md for prompt exploration.
