"""Jinja2 template environment loader for Slack bot commands."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
