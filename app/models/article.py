from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)  # Markdown source
    summary = Column(String(500), default="")
    visibility = Column(String(20), default="public")  # public | private | restricted | draft
    password_hash = Column(String(128), nullable=True)  # optional article password
    is_published = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    author = relationship("User", backref="articles")
    access_list = relationship("ArticleAccess", back_populates="article", cascade="all, delete-orphan")


class ArticleAccess(Base):
    """Grant restricted-article access to specific users."""
    __tablename__ = "article_access"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    article = relationship("Article", back_populates="access_list")
    user = relationship("User", backref="accessible_articles")
