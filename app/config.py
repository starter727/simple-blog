from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "My Blog"
    DEBUG: bool = False  # 生产环境默认关闭调试

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'blog.db'}"

    # Content source configuration
    # Option 1: Local directory (default)
    CONTENT_DIR: str = str(BASE_DIR / "content")

    # Option 2: GitHub repository (set this to use remote content)
    # Format: "owner/repo" (e.g., "starter727/blog-content")
    GITHUB_CONTENT_REPO: Optional[str] = None

    # Path to content directory in GitHub repository
    GITHUB_CONTENT_PATH: str = "content"

    # Branch to use (default: main)
    GITHUB_CONTENT_BRANCH: str = "main"

    # GitHub Token for private repositories (required for private repos)
    # Generate at: https://github.com/settings/tokens
    # Required permissions: repo (Full control of private repositories)
    GITHUB_TOKEN: Optional[str] = None

    # Auth - 必须通过环境变量或 .env 文件提供
    SECRET_KEY: str = Field(
        ...,  # ... 表示必填
        description="JWT 签名密钥，必须设置一个随机字符串"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Admin (initialized on first run)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = Field(
        ...,  # 必填
        description="管理员密码，首次运行时创建管理员账号"
    )

    # Webhook secret for GitHub
    WEBHOOK_SECRET: str = ""

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def use_github_content(self) -> bool:
        """Check if we should use GitHub as content source."""
        return self.GITHUB_CONTENT_REPO is not None


settings = Settings()
