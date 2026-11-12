"""Tests for AI prompt template escaping."""

import pytest
from jinja2 import DictLoader

from apps.ai.template_loader import env


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("prompt.jinja", "<#C123> & <@U123>"),
        ("page.html", "&lt;#C123&gt; &amp; &lt;@U123&gt;"),
        ("document.xml", "&lt;#C123&gt; &amp; &lt;@U123&gt;"),
    ],
)
def test_named_template_escaping(name, expected):
    template_env = env.overlay(loader=DictLoader({name: "{{ value }}"}))

    assert template_env.get_template(name).render(value="<#C123> & <@U123>") == expected


def test_inline_templates_escape_html():
    assert env.from_string("{{ value }}").render(value="<script>") == "&lt;script&gt;"
