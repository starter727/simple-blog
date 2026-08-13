"""Load articles from content/ directory with YAML frontmatter parsing.

Supports nested directories:
  content/tech/python-basics.md       → slug: tech/python-basics
  content/notes/daily/2026-08-11.md   → slug: notes/daily/2026-08-11
  content/hello-world.md              → slug: hello-world

Supports two modes:
  1. Local: Read from content/ directory (default)
  2. Remote: Read from GitHub repository (set GITHUB_CONTENT_REPO)
"""

from __future__ import annotations

import re
import base64
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import httpx
import yaml

from app.config import settings


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


def _fetch_github_file(repo: str, path: str, branch: str = "main") -> Optional[str]:
    """Fetch file content from GitHub repository.

    Args:
        repo: GitHub repository in format "owner/repo"
        path: File path relative to repository root
        branch: Branch name (default: main)

    Returns:
        File content as string, or None if not found
    """
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                return response.text
            return None
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return None


def _fetch_github_directory(repo: str, path: str = "", branch: str = "main") -> list[str]:
    """Fetch list of files in GitHub directory.

    Args:
        repo: GitHub repository in format "owner/repo"
        path: Directory path relative to repository root
        branch: Branch name (default: main)

    Returns:
        List of file paths (relative to repository root)
    """
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                items = response.json()
                return [item["path"] for item in items if item["type"] == "file"]
            return []
    except Exception as e:
        print(f"[WARN] Failed to fetch directory {url}: {e}")
        return []


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


def load_article_from_github(repo: str, rel_path: str, branch: str = "main") -> Optional[ArticleFile]:
    """Load a single .md file from GitHub and return parsed ArticleFile.

    Args:
        repo: GitHub repository in format "owner/repo"
        rel_path: File path relative to repository root (e.g., "content/tech/python-basics.md")
        branch: Branch name (default: main)

    Returns:
        ArticleFile if successful, None otherwise
    """
    raw = _fetch_github_file(repo, rel_path, branch)
    if not raw:
        return None

    meta, body = _parse_frontmatter(raw)
    slug_from_path = _make_slug(rel_path)

    return ArticleFile(
        filepath=Path(rel_path),  # Use relative path as identifier
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


def load_all_articles_from_github(repo: str, content_path: str = "content", branch: str = "main") -> list[ArticleFile]:
    """Load all .md files from GitHub repository.

    Args:
        repo: GitHub repository in format "owner/repo"
        content_path: Path to content directory in repository
        branch: Branch name (default: main)

    Returns:
        List of ArticleFile objects
    """
    articles = []

    # Get list of all files in content directory
    files = _fetch_github_directory(repo, content_path, branch)

    for file_path in files:
        # Only process .md files
        if not file_path.endswith(".md"):
            continue

        # Skip files starting with _ (drafts, partials, etc.)
        filename = Path(file_path).name
        if filename.startswith("_"):
            continue

        # Load article
        article = load_article_from_github(repo, file_path, branch)
        if article:
            articles.append(article)
        else:
            print(f"[WARN] Failed to load {file_path} from GitHub")

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


def find_article_from_github(repo: str, slug: str, content_path: str = "content", branch: str = "main") -> Optional[ArticleFile]:
    """Find and load article from GitHub by slug.

    Args:
        repo: GitHub repository in format "owner/repo"
        slug: Article slug to find
        content_path: Path to content directory in repository
        branch: Branch name (default: main)

    Returns:
        ArticleFile if found, None otherwise
    """
    articles = load_all_articles_from_github(repo, content_path, branch)
    for article in articles:
        if article.slug == slug:
            return article
    return None
