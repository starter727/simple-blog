from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "My Blog"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'blog.db'}"

    # Content (separate Git repo path)
    CONTENT_DIR: str = str(BASE_DIR / "content")

    # Auth
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Admin (initialized on first run)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # Webhook secret for GitHub
    WEBHOOK_SECRET: str = ""

    model_config = {"env_file": str(BASE_DIR / ".env"), "extra": "ignore"}


settings = Settings()
