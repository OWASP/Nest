"""Jinja2 template environment loader for AI agent backstories."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

# Agent .jinja prompts are plain text and intentionally do not autoescape.
env = Environment(  # NOSEMGREP: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2  # noqa: E501
    loader=FileSystemLoader(TEMPLATES_DIR),
    # Escape HTML/XML templates and templates created from inline strings.
    autoescape=select_autoescape(),
)
