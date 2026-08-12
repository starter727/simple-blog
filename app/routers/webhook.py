"""Webhook endpoint: GitHub push → git pull → sync."""

import hashlib
import hmac
import subprocess
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
    """Receive GitHub push webhook, pull latest, and sync articles."""

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

    # git pull in content directory
    try:
        result = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=str(content_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={"error": "git pull failed", "detail": result.stderr},
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Sync articles to database
    stats = sync_articles(db)

    return {
        "status": "ok",
        "git": result.stdout.strip(),
        "sync": stats,
    }
