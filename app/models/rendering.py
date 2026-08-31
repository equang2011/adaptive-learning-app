from pydantic import BaseModel


class ParagraphBlock(BaseModel):
    id: str
    source_field: str
    text: str

class TaggedSection(BaseModel):
    heading: str
    paragraphs: list[ParagraphBlock]

class TaggedLesson(BaseModel):
    introduction: list[ParagraphBlock]
    sections: list[TaggedSection]
    example: list[ParagraphBlock]