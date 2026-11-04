"""Jinja2 template environment loader for AI agent backstories."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

# Agent prompts intentionally use Jinja; markup and inline strings still escape.
env = Environment(  # NOSEMGREP: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2  # noqa: E501
    loader=FileSystemLoader(TEMPLATES_DIR),
    # Prompt files are plain text; escape HTML/XML and inline templates.
    autoescape=select_autoescape(),
)
