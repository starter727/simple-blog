"""Sync Markdown files to database.

Supports two modes:
  1. Local: Read from content/ directory (default)
  2. Remote: Read from GitHub repository (set GITHUB_CONTENT_REPO)

Key rule: new articles (not in DB) default to visibility='private'.
Existing articles keep their DB metadata; only content is refreshed.
"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.article import Article
from app.models.user import User
from app.services.content_loader import (
    load_all_articles,
    load_all_articles_from_github,
    find_article_file,
    load_article,
    ArticleFile,
)

content_dir = Path(settings.CONTENT_DIR)


def sync_articles(db: Session) -> dict:
    """
    Scan content source and sync with database.
    Returns {created: int, updated: int, unchanged: int, errors: list}.
    """
    # Load articles based on configuration
    if settings.use_github_content:
        print(f"📡 Loading content from GitHub: {settings.GITHUB_CONTENT_REPO}")
        files = load_all_articles_from_github(
            repo=settings.GITHUB_CONTENT_REPO,
            content_path=settings.GITHUB_CONTENT_PATH,
            branch=settings.GITHUB_CONTENT_BRANCH,
            token=settings.GITHUB_TOKEN,
        )
    else:
        print(f"📁 Loading content from local: {content_dir}")
        files = load_all_articles(content_dir)

    stats = {"created": 0, "updated": 0, "unchanged": 0, "errors": []}

    # Get admin user (author for all synced articles)
    admin = db.query(User).filter(User.is_admin == True).first()
    if not admin:
        raise RuntimeError("No admin user found. Run init_admin.py first.")

    existing_slugs = {a.slug: a for a in db.query(Article).all()}
    existing_contents = {a.content: a for a in db.query(Article).all()}
    file_slugs = set()

    # Check for duplicate slugs in this batch
    seen_slugs = {}
    for af in files:
        if af.slug in seen_slugs:
            stats["errors"].append(
                f"⚠️  重复的 slug '{af.slug}': "
                f"'{seen_slugs[af.slug].filepath}' 和 '{af.filepath}'"
            )
            continue
        seen_slugs[af.slug] = af

    for af in files:
        # Skip files with duplicate slugs
        if af.slug in [e.split("'")[1] for e in stats["errors"] if "'" in e]:
            continue

        file_slugs.add(af.slug)
        existing = existing_slugs.get(af.slug)

        if existing is None:
            # Check if content matches any existing article (file moved or slug changed)
            content_match = existing_contents.get(af.content)
            if content_match:
                # File moved or slug changed! Migrate permissions
                print(f"🔄 检测到 slug 变更: {content_match.slug} → {af.slug}")
                content_match.slug = af.slug
                content_match.title = af.title
                content_match.summary = af.summary
                stats["updated"] += 1
                print(f"✅ 已迁移权限: {af.slug}")
            else:
                # Truly new article
                # 使用文件中的 visibility，如果没有则默认为 draft
                visibility = af.visibility if af.visibility in ["public", "private", "restricted", "draft"] else "draft"

                # Draft 文章不保存内容，只保存元数据
                if visibility == "draft":
                    content = ""
                    summary = ""
                    print(f"📝 Draft 文章，仅保存元数据: {af.slug}")
                else:
                    content = af.content
                    summary = af.summary

                article = Article(
                    title=af.title,
                    slug=af.slug,
                    content=content,
                    summary=summary,
                    visibility=visibility,
                    password_hash=None,
                    is_published=af.published,
                    author_id=admin.id,
                )
                db.add(article)
                stats["created"] += 1
                print(f"✅ 创建新文章: {af.slug} (visibility: {visibility})")
        else:
            # EXISTING article → keep DB metadata, refresh content
            changed = False

            # Draft 文章不更新内容
            if existing.visibility == "draft":
                # 只更新标题
                if existing.title != af.title:
                    existing.title = af.title
                    changed = True
                print(f"📝 Draft 文章，仅更新标题: {af.slug}")
            else:
                # 正常更新内容
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
                print(f"📝 更新文章: {af.slug}")
            else:
                stats["unchanged"] += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        stats["errors"].append(f"❌ 数据库错误: {str(e)}")

    return stats


def sync_articles_with_migration(db: Session) -> dict:
    """
    Smart sync: detect moved files and migrate permissions.
    """
    files = load_all_articles(content_dir)
    stats = {"created": 0, "updated": 0, "migrated": 0, "unchanged": 0}

    admin = db.query(User).filter(User.is_admin == True).first()
    if not admin:
        raise RuntimeError("No admin user found.")

    existing_slugs = {a.slug: a for a in db.query(Article).all()}
    existing_contents = {a.content: a for a in db.query(Article).all()}

    for af in files:
        existing = existing_slugs.get(af.slug)

        if existing is None:
            # Check if content matches any existing article (file moved)
            content_match = existing_contents.get(af.content)
            if content_match:
                # File moved! Migrate permissions
                content_match.slug = af.slug
                content_match.title = af.title
                content_match.summary = af.summary
                stats["migrated"] += 1
            else:
                # Truly new article
                article = Article(
                    title=af.title,
                    slug=af.slug,
                    content=af.content,
                    summary=af.summary,
                    visibility="private",
                    password_hash=None,
                    is_published=af.published,
                    author_id=admin.id,
                )
                db.add(article)
                stats["created"] += 1
        else:
            # Update existing article
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


def sync_single_article(db: Session, slug: str) -> bool:
    """
    Sync a single article's content from source.
    Used when changing visibility from draft to other.
    Returns True if successful.
    """
    try:
        # Load article from source
        if settings.use_github_content:
            from app.services.content_loader import find_article_from_github
            af = find_article_from_github(
                repo=settings.GITHUB_CONTENT_REPO,
                slug=slug,
                content_path=settings.GITHUB_CONTENT_PATH,
                branch=settings.GITHUB_CONTENT_BRANCH,
            )
        else:
            filepath = find_article_file(content_dir, slug)
            if filepath:
                af = load_article(filepath, content_dir)
            else:
                af = None

        if not af:
            print(f"⚠️ 未找到文章文件: {slug}")
            return False

        # Update article in database
        article = db.query(Article).filter(Article.slug == slug).first()
        if not article:
            print(f"⚠️ 数据库中未找到文章: {slug}")
            return False

        article.content = af.content
        article.summary = af.summary
        article.title = af.title
        db.commit()

        print(f"✅ 已同步文章内容: {slug}")
        return True

    except Exception as e:
        print(f"❌ 同步文章失败: {slug} - {str(e)}")
        db.rollback()
        return False
