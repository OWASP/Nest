"""Verify escaping for prompt and markup templates."""

import pytest
from jinja2 import DictLoader

from apps.ai.template_loader import env


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("prompt.jinja", "<b>A & B</b>"),
        ("page.html", "&lt;b&gt;A &amp; B&lt;/b&gt;"),
        ("document.xml", "&lt;b&gt;A &amp; B&lt;/b&gt;"),
    ],
)
def test_template_escaping(filename, expected):
    environment = env.overlay(loader=DictLoader({filename: "{{ value }}"}))
    assert environment.get_template(filename).render(value="<b>A & B</b>") == expected


def test_inline_template_escaping():
    assert env.from_string("{{ value }}").render(value="<b>A & B</b>") == (
        "&lt;b&gt;A &amp; B&lt;/b&gt;"
    )
