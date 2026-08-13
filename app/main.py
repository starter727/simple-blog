"""FastAPI blog application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db, SessionLocal
from app.models.user import User
from app.services.permission import hash_password
from app.routers import auth, articles, admin, webhook

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.APP_NAME)

# Session middleware (for password-unlock state)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="blog_session",
    max_age=86400,
)

# Static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR.parent / "static")), name="static")

# Routers
app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(admin.router)
app.include_router(webhook.router)


@app.on_event("startup")
async def startup():
    # 初始化数据库表
    init_db()

    # 创建管理员账号（如果不存在）
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ 管理员账号已创建: {settings.ADMIN_USERNAME}")
        else:
            print(f"ℹ️  管理员账号已存在: {settings.ADMIN_USERNAME}")
    except Exception as e:
        print(f"❌ 创建管理员账号失败: {e}")
        db.rollback()
    finally:
        db.close()
