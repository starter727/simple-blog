"""Markdown rendering with extensions."""

import markdown
from markupsafe import Markup
from app.services.wikilink_ext import WikiLinkExtension


def render_markdown(text: str) -> str:
    """Convert Markdown text to safe HTML."""
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "footnotes",
            WikiLinkExtension(),
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "linenums": False,
            },
        },
    )
    html = md.convert(text)
    return Markup(html)
