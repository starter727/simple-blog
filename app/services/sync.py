"""Sync Markdown files from content/ directory to database.

Key rule: new articles (not in DB) default to visibility='private'.
Existing articles keep their DB metadata; only content is refreshed from file.
"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.article import Article
from app.models.user import User
from app.services.content_loader import load_all_articles, ArticleFile

content_dir = Path(settings.CONTENT_DIR)


def sync_articles(db: Session) -> dict:
    """
    Scan content directory and sync with database.
    Returns {created: int, updated: int, unchanged: int}.
    """
    files = load_all_articles(content_dir)
    stats = {"created": 0, "updated": 0, "unchanged": 0}

    # Get admin user (author for all synced articles)
    admin = db.query(User).filter(User.is_admin == True).first()
    if not admin:
        raise RuntimeError("No admin user found. Run init_admin.py first.")

    existing_slugs = {a.slug: a for a in db.query(Article).all()}
    file_slugs = set()

    for af in files:
        file_slugs.add(af.slug)
        existing = existing_slugs.get(af.slug)

        if existing is None:
            # NEW article → always private by default
            article = Article(
                title=af.title,
                slug=af.slug,
                content=af.content,
                summary=af.summary,
                visibility="private",          # ← 默认仅自己可见
                password_hash=None,
                is_published=af.published,
                author_id=admin.id,
            )
            db.add(article)
            stats["created"] += 1
        else:
            # EXISTING article → keep DB metadata, refresh content
            changed = False
            if existing.content != af.content:
                existing.content = af.content
                changed = True
            if existing.title != af.title:
                existing.title = af.title
                changed = True
            if existing.summary != af.summary:
                existing.summary = af.summary
                changed = True
            if changed:
                stats["updated"] += 1
            else:
                stats["unchanged"] += 1

    db.commit()
    return stats
