
from app.models.lesson import Lesson
from app.models.rendering import ParagraphBlock


def build_paragraph_blocks(lesson: Lesson) -> list[ParagraphBlock]:
    """
    Convert learner-facing lesson prose into stable paragraph blocks.

    Display/order contract:
    1. introduction
    2. section contents, in section order
    3. example
    4. key takeaways

    Split prose fields on "\\n\\n".
    Assign global IDs p1, p2, p3... in display order.
    Preserve source_field so future citation results can point back to
    the paragraph rendered in the lesson.
    """

    counter = 1
    res = []

    # 1. Introduction
    intro_parts = lesson.introduction.split("\n\n")

    for paragraph in intro_parts:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        new_block = ParagraphBlock(
            id=f"p{counter}",
            source_field="introduction",
            text=paragraph,
        )
        res.append(new_block)
        counter += 1

    # TODO 2: sections
    # for section_index, section in enumerate(lesson.sections):
    #     split section.content on "\n\n"
    #     source_field = f"sections[{section_index}].content"

    # TODO 3: example
    # split lesson.example on "\n\n"
    # source_field = "example"

    # TODO 4: key takeaways
    # each takeaway can initially be one block
    # source_field = f"key_takeaways[{takeaway_index}]"

    return res
