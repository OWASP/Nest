"""Tests for the url_filters template tag library."""

import pytest
from django.template import Context, Template


class TestSafeUrlFilter:
    """Tests for the safe_url template filter."""

    @staticmethod
    def _render(url):
        """Render a template using the safe_url filter with the given URL."""
        template = Template("{% load url_filters %}{{ url|safe_url }}")
        return template.render(Context({"url": url}))

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("https://github.com/OWASP/Nest/issues/1", "https://github.com/OWASP/Nest/issues/1"),
            ("https://example.com", "https://example.com"),
            ("http://example.com", "http://example.com"),
            ("https://example.com/path?query=1", "https://example.com/path?query=1"),
        ],
    )
    def test_safe_url_allows_valid_urls(self, url, expected):
        """Test that valid http/https URLs pass through unchanged."""
        assert self._render(url) == expected

    @pytest.mark.parametrize(
        "url",
        [
            "javascript:alert(1)",
            "javascript:alert(document.cookie)",
            "data:text/html,<script>alert(1)</script>",
            "ftp://example.com",
            "file:///etc/passwd",
        ],
    )
    def test_safe_url_blocks_dangerous_urls(self, url):
        """Test that dangerous URL schemes are replaced with '#'."""
        assert self._render(url) == "#"

    @pytest.mark.parametrize(
        "url",
        [
            "",
            None,
        ],
    )
    def test_safe_url_handles_empty_values(self, url):
        """Test that empty or None values return '#'."""
        assert self._render(url) == "#"
