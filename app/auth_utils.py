"""JWT token helpers & current-user dependency."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Request, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Return the logged-in user or None (does NOT raise)."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()


def require_admin(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Dependency that raises 403 if the current user is not admin."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=403, detail="未登录")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403, detail="无效凭证")
    except JWTError:
        raise HTTPException(status_code=403, detail="无效凭证")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
