"""Jinja2 template environment loader."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
SLACK_TEMPLATES_DIR = BASE_DIR / "slack" / "templates"
VIDEO_TEMPLATES_DIR = BASE_DIR / "owasp" / "templates" / "video"

# Suppress false positive Flask security warning.
slack_env = Environment(  # NOSEMGREP: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2  # noqa: E501
    loader=FileSystemLoader(SLACK_TEMPLATES_DIR), autoescape=True
)
video_env = Environment(  # NOSEMGREP: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2  # noqa: E501
    loader=FileSystemLoader(VIDEO_TEMPLATES_DIR), autoescape=True
)
