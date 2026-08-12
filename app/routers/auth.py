"""Authentication routes: login / logout."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.permission import verify_password
from app.auth_utils import create_access_token
from app.templates_config import templates

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request, "auth/login.html", {"error": "用户名或密码错误"},
            status_code=401,
        )
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/admin/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
