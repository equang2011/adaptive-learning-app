import bleach
import markdown
from markupsafe import Markup

ALLOWED_TAGS = [
    "p", "br", "hr",
    "strong", "em", "code", "pre",
    "h1", "h2", "h3", "h4",
    "ul", "ol", "li",
    "blockquote",
    "a",
    "table", "thead", "tbody", "tr", "th", "td",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}


def render_markdown(text: str) -> Markup:
    """Render LLM-generated markdown to sanitized HTML.

    LLM output is untrusted content, so this always sanitizes the
    resulting HTML with an allowlist rather than trusting `markdown`'s
    own output directly.
    """
    html = markdown.markdown(text or "", extensions=["fenced_code", "tables"])
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
    return Markup(clean_html)
