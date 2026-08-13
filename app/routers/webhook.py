"""Webhook endpoint: GitHub push → sync."""

import hashlib
import hmac
from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.sync import sync_articles

router = APIRouter(tags=["webhook"])

content_dir = Path(settings.CONTENT_DIR)


@router.post("/webhook/github")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    """Receive GitHub push webhook and sync articles."""

    # Verify webhook secret if configured
    secret = settings.WEBHOOK_SECRET
    if secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        body = await request.body()
        expected = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Sync articles to database
    # If using GitHub content, it will fetch from GitHub API
    # If using local content, it will read from local directory
    stats = sync_articles(db)

    return {
        "status": "ok",
        "sync": stats,
    }
