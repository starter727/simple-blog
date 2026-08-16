"""Article permission logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

import bcrypt

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# Permission check
# ---------------------------------------------------------------------------

class AccessResult:
    """Return value from check_access."""
    DENIED = "denied"
    ALLOWED = "allowed"
    NEED_PASSWORD = "need_password"

    def __init__(self, status: str):
        self.status = status

    @property
    def ok(self) -> bool:
        return self.status == self.ALLOWED


def check_article_access(
    article: "Article",
    current_user: "User | None",
    provided_password: str | None = None,
) -> AccessResult:
    """
    Determine whether *current_user* may view *article*.

    Priority:
      1. Author always has access.
      2. visibility == "draft"  → only author (completely hidden from lists).
      3. visibility == "private"  → only author (visible in lists but content hidden).
      4. visibility == "restricted" → must be in ArticleAccess list.
      5. Article has a password → caller must supply it.
      6. Otherwise → allowed.
    """

    # 1. Author
    if current_user and current_user.id == article.author_id:
        return AccessResult(AccessResult.ALLOWED)

    # 2. Draft (completely hidden)
    if article.visibility == "draft":
        return AccessResult(AccessResult.DENIED)

    # 3. Private
    if article.visibility == "private":
        return AccessResult(AccessResult.DENIED)

    # 4. Restricted
    if article.visibility == "restricted":
        if not current_user:
            return AccessResult(AccessResult.DENIED)
        allowed_ids = {a.user_id for a in article.access_list}
        if current_user.id not in allowed_ids:
            return AccessResult(AccessResult.DENIED)

    # 5. Password-protected
    if article.password_hash:
        if provided_password and verify_password(provided_password, article.password_hash):
            return AccessResult(AccessResult.ALLOWED)
        return AccessResult(AccessResult.NEED_PASSWORD)

    return AccessResult(AccessResult.ALLOWED)
