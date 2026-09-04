"""Tests for dependency-free Slack text helpers."""

import unicodedata

import pytest

from apps.slack.common.text import (
    fit_quoted_mrkdwn,
    prefix_by_visible_len,
    preview_text,
    quote_mrkdwn,
)


class TestFitQuotedMrkdwn:
    def test_non_positive_limit(self):
        """Test non-positive limits return an empty string."""
        assert fit_quoted_mrkdwn("hello", limit=0) == ""
        assert fit_quoted_mrkdwn("hello", limit=-1) == ""

    def test_under_and_exact_limit(self):
        """Test under-limit and exact-limit quoted text are kept in full."""
        assert fit_quoted_mrkdwn("ab", limit=10) == ">ab"
        assert fit_quoted_mrkdwn("ab", limit=3) == ">ab"

    def test_over_limit_truncates_before_quoting(self):
        """Test over-limit input is shortened so the quoted result fits."""
        assert fit_quoted_mrkdwn("abcd", limit=3) == ">ab"
        assert len(fit_quoted_mrkdwn("abcdefghij", limit=5)) <= 5

    def test_sanitizer_expansion_is_accounted_for(self):
        """Test ampersand expansion is included in the fitted length."""
        # "&" becomes "&amp;" (5 chars) then quoted as ">&amp;" (6 chars).
        assert fit_quoted_mrkdwn("&", limit=6) == ">&amp;"
        assert fit_quoted_mrkdwn("&", limit=5) == ""

    def test_multiline_quoting(self):
        """Test each line is quoted and the combined length stays in budget."""
        assert fit_quoted_mrkdwn("a\nb", limit=10) == ">a\n>b"
        assert fit_quoted_mrkdwn("a\nb\nc", limit=5) == ">a\n>b"


class TestPrefixByVisibleLen:
    def test_keeps_combining_marks_with_base_character(self):
        """Test combining marks stay attached when truncating by visible length."""
        decomposed = "a\u0301b"
        assert prefix_by_visible_len(decomposed, limit=1) == "a\u0301"
        assert prefix_by_visible_len(decomposed, limit=2) == decomposed

    @pytest.mark.parametrize("limit", [0, -1])
    def test_non_positive_limit(self, limit):
        """Test non-positive limits return an empty prefix."""
        assert prefix_by_visible_len("abc", limit=limit) == ""


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


class TestQuoteMrkdwn:
    def test_prefixes_each_line(self):
        """Test each line is quoted for Slack multiline blockquotes."""
        assert quote_mrkdwn("a\nb") == ">a\n>b"
        assert quote_mrkdwn("") == ""
