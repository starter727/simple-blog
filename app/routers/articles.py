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
from app.services.content_loader import find_article_file, load_article
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


@router.get("/")
async def article_list(request: Request, db: Session = Depends(get_db)):
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

    # Load content from file (falls back to DB content if file not found)
    content = article.content
    filepath = find_article_file(content_dir, slug)
    if filepath:
        try:
            af = load_article(filepath, content_dir)
            content = af.content
        except Exception:
            pass  # fall back to DB content

    html_content = render_markdown(content)
    category = _extract_category(article.slug)
    return templates.TemplateResponse(
        request, "articles/detail.html",
        {"article": article, "html_content": html_content, "current_user": user, "category": category},
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
