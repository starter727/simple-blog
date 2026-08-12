"""Shared Jinja2 templates instance."""

from pathlib import Path
from fastapi.templating import Jinja2Templates

_templates_dir = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))
