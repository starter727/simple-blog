"""Public article routes: list & detail."""

from pathlib import Path

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.article import Article
from app.auth_utils import get_current_user
from app.services.permission import check_article_access, AccessResult
from app.services.markdown_service import render_markdown
from app.services.content_loader import (
    find_article_file,
    load_article,
    find_article_from_github,
)
from app.templates_config import templates

router = APIRouter(tags=["articles"])

content_dir = Path(settings.CONTENT_DIR)


def _extract_category(slug: str) -> str:
    """Extract first-level directory from slug as category.

    "tech/python-basics"  → "tech"
    "notes/daily/2026-08-11" → "notes"
    "hello-world" → ""
    """
    parts = slug.split("/")
    if len(parts) >= 2:
        return parts[0]
    return ""


def _extract_breadcrumb(slug: str) -> list[dict]:
    """Extract breadcrumb path from slug.

    "tech/python-basics"  → [{"name": "tech", "path": "tech"}, {"name": "python-basics", "path": "tech/python-basics"}]
    "notes/daily/2026-08-11" → [{"name": "notes", "path": "notes"}, {"name": "daily", "path": "notes/daily"}, {"name": "2026-08-11", "path": "notes/daily/2026-08-11"}]
    """
    parts = slug.split("/")
    breadcrumb = []
    for i, part in enumerate(parts):
        path = "/".join(parts[:i+1])
        breadcrumb.append({"name": part, "path": path})
    return breadcrumb


@router.get("/")
async def article_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user and user.is_admin:
        # 管理员可以看到所有文章（除了 draft）
        articles = (
            db.query(Article)
            .filter(Article.visibility != "draft")
            .order_by(Article.created_at.desc())
            .all()
        )
    else:
        # 普通用户只能看到公开且已发布的文章
        articles = (
            db.query(Article)
            .filter(
                Article.is_published == True,
                Article.visibility == "public"
            )
            .order_by(Article.created_at.desc())
            .all()
        )

    # Extract categories
    categories = sorted(set(
        _extract_category(a.slug) for a in articles if _extract_category(a.slug)
    ))

    return templates.TemplateResponse(
        request, "articles/list.html", {
            "articles": articles,
            "current_user": user,
            "categories": categories,
            "current_category": None,
        },
    )


@router.get("/category/{category}")
async def article_list_by_category(request: Request, category: str, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user and user.is_admin:
        articles = (
            db.query(Article)
            .order_by(Article.created_at.desc())
            .all()
        )
    else:
        articles = (
            db.query(Article)
            .filter(Article.is_published == True, Article.visibility == "public")
            .order_by(Article.created_at.desc())
            .all()
        )

    # Filter by category (first-level directory)
    filtered = [a for a in articles if _extract_category(a.slug) == category]

    categories = sorted(set(
        _extract_category(a.slug) for a in articles if _extract_category(a.slug)
    ))

    return templates.TemplateResponse(
        request, "articles/list.html", {
            "articles": filtered,
            "current_user": user,
            "categories": categories,
            "current_category": category,
        },
    )


@router.get("/article/{slug:path}")
async def article_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    # Find article in DB
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        return templates.TemplateResponse(
            request, "articles/not_found.html", {"current_user": user},
            status_code=404,
        )

    # Draft 文章只有作者能访问，但不显示内容
    if article.visibility == "draft":
        if not user or user.id != article.author_id:
            return templates.TemplateResponse(
                request, "articles/not_found.html", {"current_user": user},
                status_code=404,
            )
        # Draft 文章：只显示标题，不显示内容
        category = _extract_category(article.slug)
        breadcrumb = _extract_breadcrumb(article.slug)
        return templates.TemplateResponse(
            request, "articles/draft.html",
            {"article": article, "current_user": user, "category": category, "breadcrumb": breadcrumb},
        )

    # Check permission
    already_unlocked = request.session.get(f"unlocked_{article.id}", False)
    result = check_article_access(article, user)
    if result.status == AccessResult.NEED_PASSWORD and not already_unlocked:
        return templates.TemplateResponse(
            request, "articles/password_prompt.html",
            {"article": article, "current_user": user, "error": None},
        )
    if not result.ok and not already_unlocked:
        return templates.TemplateResponse(
            request, "articles/forbidden.html", {"current_user": user},
            status_code=403,
        )

    # Load content from source (falls back to DB content if not found)
    content = article.content

    if settings.use_github_content:
        # Load from GitHub
        try:
            af = find_article_from_github(
                repo=settings.GITHUB_CONTENT_REPO,
                slug=slug,
                content_path=settings.GITHUB_CONTENT_PATH,
                branch=settings.GITHUB_CONTENT_BRANCH,
            )
            if af:
                content = af.content
        except Exception:
            pass  # fall back to DB content
    else:
        # Load from local file
        filepath = find_article_file(content_dir, slug)
        if filepath:
            try:
                af = load_article(filepath, content_dir)
                content = af.content
            except Exception:
                pass  # fall back to DB content

    html_content = render_markdown(content)
    category = _extract_category(article.slug)
    breadcrumb = _extract_breadcrumb(article.slug)
    return templates.TemplateResponse(
        request, "articles/detail.html",
        {"article": article, "html_content": html_content, "current_user": user, "category": category, "breadcrumb": breadcrumb},
    )


@router.post("/article/{slug:path}/unlock")
async def unlock_article(
    request: Request,
    slug: str,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        return RedirectResponse(url="/", status_code=303)
    result = check_article_access(article, user, provided_password=password)
    if result.ok:
        request.session[f"unlocked_{article.id}"] = True
        return RedirectResponse(url=f"/article/{slug}", status_code=303)
    return templates.TemplateResponse(
        request, "articles/password_prompt.html",
        {"article": article, "current_user": user, "error": "密码错误"},
    )
