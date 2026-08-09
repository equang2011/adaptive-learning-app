from html import escape
from pathlib import Path

from app.models.lesson import Lesson

ROOT = Path(__file__).resolve().parents[1]
LESSON_DIR = ROOT / "data" / "lessons"

LESSON_FILE = LESSON_DIR / "lesson_m4-s1-l3_v1_tencent_hy3_20260808_200933.json"

OUTPUT_FILE = ROOT / "lesson_preview.html"


def render_lesson(lesson: Lesson) -> str:
    sections_html = ""

    for section in lesson.sections:
        sections_html += f"""
        <section>
            <h2>{escape(section.heading)}</h2>
            <p>{escape(section.content)}</p>
        </section>
        """
    takeaways_html = ""

    for takeaway in lesson.key_takeaways:
        takeaways_html += f"<li>{escape(takeaway)}</li>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{escape(lesson.title)}</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 760px;
                margin: 40px auto;
                padding: 0 20px;
                line-height: 1.6;
            }}

            .metadata {{
                color: #666;
            }}

            .objective {{
                padding: 16px;
                background: #f4f4f4;
                border-radius: 8px;
            }}

            section {{
                margin-top: 32px;
            }}

            p {{
                white-space: pre-wrap;
            }}

            .example {{
                margin-top: 32px;
                padding: 16px;
                background: #f4f4f4;
                border-radius: 8px;
                white-space: pre-wrap;
            }}
        </style>
    </head>

    <body>
        <h1>{escape(lesson.title)}</h1>

        <p class="metadata">
            Estimated study time: {lesson.estimated_minutes} minutes
        </p>

        <div class="objective">
            <strong>Objective:</strong>
            {escape(lesson.objective)}
        </div>

        <p>{escape(lesson.introduction)}</p>

        {sections_html}

        <div class="example">
            <h2>Example</h2>
            {escape(lesson.example)}
        </div>

        <h2>Key Takeaways</h2>
        <ul>
            {takeaways_html}
        </ul>
    </body>
    </html>
    """

def main():
    lesson_json = LESSON_FILE.read_text(encoding="utf-8")

    lesson = Lesson.model_validate_json(lesson_json)

    html = render_lesson(lesson)

    OUTPUT_FILE.write_text(
        html,
        encoding="utf-8")
    print("saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()