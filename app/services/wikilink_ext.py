"""Markdown extension: convert [[slug]] to <a href="/article/slug">slug</a>.

Supports:
  [[hello-world]]          → <a href="/article/hello-world">hello-world</a>
  [[hello-world|Hello!]]   → <a href="/article/hello-world">Hello!</a>
  [[tech/python-basics]]   → <a href="/article/tech/python-basics">tech/python-basics</a>
"""

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree


class WikiLinkProcessor(InlineProcessor):
    """Convert [[slug]] or [[slug|label]] to clickable links."""

    def handleMatch(self, m, data):
        slug = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else slug

        a = etree.Element("a")
        a.set("href", f"/article/{slug}")
        a.set("class", "wikilink")
        a.text = label
        return a, m.start(0), m.end(0)


class WikiLinkExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            WikiLinkProcessor(r"\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]", md),
            "wikilink",
            175,
        )
