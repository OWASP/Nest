"""Jinja2 template environment loader for AI agent backstories."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    # Prompt files are plain text; escape HTML/XML and inline templates.
    autoescape=select_autoescape(),
)
