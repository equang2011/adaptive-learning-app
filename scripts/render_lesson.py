import bleach
import markdown

from html import escape
from pathlib import Path

from app.models.lesson import Lesson

ROOT = Path(__file__).resolve().parents[1]
LESSON_DIR = ROOT / "data" / "lessons"

LESSON_FILE = LESSON_DIR / "lesson_m4-s1-l3_v1_tencent_hy3_20260808_200933.json"

OUTPUT_FILE = ROOT / "lesson_preview.html"


def render_markdown(text: str) -> str:
    raw_html = markdown.markdown(
        text,
        extensions=['fenced_code']
    )

    return bleach.clean(
        raw_html,
        tags=[
            "p",
            "strong",
            "em",
            "code",
            "pre",
            "ul",
            "ol",
            "li",
        ],
        strip=True,
    )



def render_lesson(lesson: Lesson) -> str:
    sections_html = ""

    for section in lesson.sections:
        sections_html += f"""
        <section>
            <h2>{escape(section.heading)}</h2>
            {render_markdown(section.content)}
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
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            max-width: 720px;
            margin: 48px auto;
            padding: 0 24px 64px;
            line-height: 1.7;
            color: #222;
            background: #fafafa;
        }}

        h1 {{
            font-size: 2.4rem;
            line-height: 1.15;
            margin-bottom: 8px;
        }}

        h2 {{
            font-size: 1.35rem;
            margin-top: 0;
        }}

        .metadata {{
            color: #666;
            margin-bottom: 24px;
        }}

        .objective {{
            padding: 18px;
            margin-bottom: 32px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
        }}

        .introduction {{
            font-size: 1.05rem;
            margin-bottom: 32px;
        }}

        section {{
            margin-top: 36px;
        }}

        .example {{
            margin-top: 40px;
            padding: 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
        }}

        code {{
            font-family: Consolas, "Courier New", monospace;
            background: #eee;
            padding: 2px 5px;
            border-radius: 4px;
        }}

        pre {{
            overflow-x: auto;
            padding: 16px;
            background: #eee;
            border-radius: 8px;
        }}

        pre code {{
            padding: 0;
            background: transparent;
        }}

        ul {{
            padding-left: 24px;
        }}

        li {{
            margin-bottom: 8px;
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

        <div class="introduction">
            {render_markdown(lesson.introduction)}
        </div>

        {sections_html}

        <div class="example">
            <h2>Example</h2>
            {render_markdown(lesson.example)}
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