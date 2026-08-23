"""Tests for dependency-free Slack text helpers."""

import unicodedata

import pytest

from apps.slack.common.text import preview_text


class TestPreviewText:
    def test_under_exact_and_over_limit(self):
        """Test truncation for under-limit, exact-limit, and over-limit inputs."""
        assert preview_text("abcd", limit=5) == "abcd"
        assert preview_text("abcde", limit=5) == "abcde"
        assert preview_text("abcdefghij", limit=5) == "ab..."

    def test_suffix_boundary_and_small_limits(self):
        """Test ellipsis is capped so the result never exceeds the limit."""
        assert preview_text("abcdefghij", limit=4) == "a..."
        assert preview_text("abcdefghij", limit=3) == "..."
        assert preview_text("abcdefghij", limit=2) == ".."
        assert preview_text("abcdefghij", limit=1) == "."

    @pytest.mark.parametrize("limit", [0, -1, -10])
    def test_non_positive_limit(self, limit):
        """Test non-positive limits return an empty preview."""
        assert preview_text("abcdefghij", limit=limit) == ""

    def test_combining_characters_match_visible_length(self):
        """Test composed and decomposed Unicode use combining-aware counting."""
        composed = "café"
        decomposed = "cafe\u0301"
        assert unicodedata.normalize("NFC", decomposed) == composed
        assert len(decomposed) > len(composed)

        assert preview_text(composed, limit=4) == composed
        assert preview_text(decomposed, limit=4) == composed
        # Visible length is 8; keep 4 base chars + ellipsis → "café..."
        assert preview_text(f"{composed}xyzz", limit=7) == f"{composed}..."
        assert preview_text(f"{decomposed}xyzz", limit=7) == f"{composed}..."

    def test_still_sanitizes_mrkdwn(self):
        """Test truncation still escapes mrkdwn-sensitive characters."""
        assert "&lt;" in preview_text("<script>")
        assert "\\*" in preview_text("hello *bold*")
