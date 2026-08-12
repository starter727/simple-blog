"""FastAPI blog application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db
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
    init_db()
