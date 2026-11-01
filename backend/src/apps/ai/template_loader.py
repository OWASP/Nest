"""Jinja2 template environment loader for AI agent backstories."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(  # nosemgrep: direct-use-of-jinja2
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=False,  # nosemgrep: incorrect-autoescape-disabled  # noqa: S701
)
