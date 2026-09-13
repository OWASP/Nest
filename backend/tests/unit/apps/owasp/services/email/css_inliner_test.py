"""Tests for HTML email CSS inlining."""

from apps.owasp.services.email.css_inliner import inline_css


class TestInlineCss:
    """Test inline_css."""

    def test_copies_class_rules_onto_tags(self):
        """Test class CSS is applied as inline styles."""
        html = (
            "<html><head><style>.title { color: #111827; }</style></head>"
            '<body><p class="title">Hello</p></body></html>'
        )

        result = inline_css(html)

        assert 'style="color: #111827"' in result or 'style="color:#111827"' in result
        assert 'class="title"' not in result
        assert "Hello" in result
