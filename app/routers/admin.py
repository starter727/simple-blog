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
    # 构建同步结果消息
    messages = []
    if stats.get("created"):
        messages.append(f"创建 {stats['created']} 篇")
    if stats.get("updated"):
        messages.append(f"更新 {stats['updated']} 篇")
    if stats.get("unchanged"):
        messages.append(f"{stats['unchanged']} 篇未变")
    if stats.get("errors"):
        messages.append(f"{len(stats['errors'])} 个错误")

    message = "、".join(messages) if messages else "无变化"
    return RedirectResponse(url=f"/admin/?synced=1&message={message}", status_code=303)


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
    clear_password: str = Form(""),
    is_published: str = Form("false"),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return RedirectResponse(url="/admin/", status_code=303)

    # 如果从 draft 改为其他可见性，需要同步内容
    if article.visibility == "draft" and visibility != "draft":
        print(f"🔄 文章从 draft 改为 {visibility}，同步内容: {article.slug}")
        # 重新同步这篇文章的内容
        from app.services.sync import sync_single_article
        sync_single_article(db, article.slug)

    article.visibility = visibility

    # 密码处理逻辑
    if clear_password == "on":
        # 清除密码保护
        article.password_hash = None
    elif password.strip():
        # 设置新密码
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
