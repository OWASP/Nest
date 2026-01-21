"""Jinja2 template environment loader."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
SLACK_TEMPLATES_DIR = BASE_DIR / "slack" / "templates"
VIDEO_TEMPLATES_DIR = BASE_DIR / "owasp" / "templates" / "video"

slack_env = Environment(loader=FileSystemLoader(SLACK_TEMPLATES_DIR), autoescape=True)
video_env = Environment(loader=FileSystemLoader(VIDEO_TEMPLATES_DIR), autoescape=True)
