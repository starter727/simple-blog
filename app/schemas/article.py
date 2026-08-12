"""Pydantic schemas for article forms (used by admin routes)."""

from pydantic import BaseModel


class ArticleCreate(BaseModel):
    title: str
    slug: str
    content: str
    summary: str = ""
    visibility: str = "public"
    password: str | None = None
    is_published: bool = False


class ArticleUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    content: str | None = None
    summary: str | None = None
    visibility: str | None = None
    password: str | None = None
    is_published: bool | None = None
