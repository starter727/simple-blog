"""Admin routes: manage article metadata & sync."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.auth_utils import require_admin
from app.services.permission import hash_password
from app.services.sync import sync_articles
from app.templates_config import templates

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------- list ----------

@router.get("/")
async def admin_list(request: Request, admin=Depends(require_admin), db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.created_at.desc()).all()
    return templates.TemplateResponse(
        request, "admin/list.html", {"articles": articles, "current_user": admin},
    )


# ---------- manual sync ----------

@router.post("/sync")
async def manual_sync(request: Request, admin=Depends(require_admin), db: Session = Depends(get_db)):
    stats = sync_articles(db)
    return RedirectResponse(url="/admin/?synced=1", status_code=303)


# ---------- edit metadata ----------

@router.get("/{article_id}/edit")
async def edit_page(request: Request, article_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return RedirectResponse(url="/admin/", status_code=303)
    return templates.TemplateResponse(
        request, "admin/editor.html", {"article": article, "current_user": admin, "error": None},
    )


@router.post("/{article_id}/edit")
async def update_metadata(
    request: Request,
    article_id: int,
    visibility: str = Form("public"),
    password: str = Form(""),
    is_published: str = Form("false"),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return RedirectResponse(url="/admin/", status_code=303)
    article.visibility = visibility
    if password.strip():
        article.password_hash = hash_password(password)
    article.is_published = is_published == "true"
    db.commit()
    return RedirectResponse(url="/admin/", status_code=303)


# ---------- delete ----------

@router.post("/{article_id}/delete")
async def delete_article(
    request: Request,
    article_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
    return RedirectResponse(url="/admin/", status_code=303)
