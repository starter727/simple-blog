"""Load articles from content/ directory with YAML frontmatter parsing.

Supports nested directories:
  content/tech/python-basics.md       → slug: tech/python-basics
  content/notes/daily/2026-08-11.md   → slug: notes/daily/2026-08-11
  content/hello-world.md              → slug: hello-world
"""

from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass, field

import yaml


@dataclass
class ArticleFile:
    """Parsed article from a .md file."""
    filepath: Path        # absolute path to .md file
    rel_path: str         # relative path from content_dir, e.g. "tech/python-basics.md"
    title: str
    slug: str             # URL slug, e.g. "tech/python-basics"
    summary: str
    visibility: str
    password: str
    published: bool
    content: str          # Markdown body (without frontmatter)
    tags: list[str] = field(default_factory=list)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _make_slug(rel_path: str) -> str:
    """Convert relative file path to URL slug.

    "tech/python-basics.md"      → "tech/python-basics"
    "notes/daily/2026-08-11.md"  → "notes/daily/2026-08-11"
    "2026-08-11-hello-world.md"  → "hello-world" (date prefix stripped from filename only)
    """
    p = Path(rel_path)
    stem = p.stem  # filename without .md
    # Strip date prefix from filename only (keep directory names intact)
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    parts = list(p.parent.parts) + [stem]
    # Filter out '.' if parent is current dir
    parts = [part for part in parts if part != "."]
    return "/".join(parts)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from markdown body."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            return meta, body
    return {}, text


def load_article(filepath: Path, content_dir: Path) -> ArticleFile:
    """Load a single .md file and return parsed ArticleFile."""
    raw = filepath.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)

    rel_path = str(filepath.relative_to(content_dir)).replace("\\", "/")
    slug_from_path = _make_slug(rel_path)

    return ArticleFile(
        filepath=filepath,
        rel_path=rel_path,
        title=meta.get("title", Path(rel_path).stem.replace("-", " ").title()),
        slug=meta.get("slug", slug_from_path),
        summary=meta.get("summary", ""),
        visibility=meta.get("visibility", "private"),
        password=meta.get("password", ""),
        published=meta.get("published", False),
        content=body,
        tags=meta.get("tags", []),
    )


def load_all_articles(content_dir: Path) -> list[ArticleFile]:
    """Recursively scan content_dir for .md files and load them."""
    articles = []
    if not content_dir.exists():
        return articles
    for filepath in sorted(content_dir.rglob("*.md")):
        # Skip files starting with _ (drafts, partials, etc.)
        if filepath.name.startswith("_"):
            continue
        try:
            articles.append(load_article(filepath, content_dir))
        except Exception as e:
            print(f"[WARN] Failed to load {filepath}: {e}")
    return articles


def find_article_file(content_dir: Path, slug: str) -> Path | None:
    """Find the .md file matching a given slug.

    Supports both frontmatter slug override and path-based slug.
    """
    for filepath in content_dir.rglob("*.md"):
        if filepath.name.startswith("_"):
            continue
        try:
            article = load_article(filepath, content_dir)
            if article.slug == slug:
                return filepath
        except Exception:
            continue
    return None
