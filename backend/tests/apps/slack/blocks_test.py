"""Tests for Slack blocks."""

from apps.slack.blocks import (
    SLACK_SECTION_MRKDWN_MAX_CHARS,
    divider,
    markdown,
    markdown_blocks,
)


class TestSlackBlocks:
    """Tests for Slack block functions."""

    def test_divider(self):
        """Test divider returns correct block structure."""
        result = divider()
        assert result == {"type": "divider"}

    def test_markdown(self):
        """Test markdown returns correct block structure."""
        text = "**Bold text** and *italic text*"
        result = markdown(text)
        assert result["type"] == "section"
        assert result["text"]["type"] == "mrkdwn"
        assert result["text"]["text"] == text

    def test_markdown_with_empty_text(self):
        """Test markdown handles empty text."""
        result = markdown("")
        assert result["text"]["text"] == ""

    def test_markdown_blocks_short_single_section(self):
        """Short text fits in one section."""
        blocks = markdown_blocks("Hello OWASP")
        assert len(blocks) == 1
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["text"] == "Hello OWASP"

    def test_markdown_blocks_empty_input(self):
        """Empty input yields no blocks."""
        assert markdown_blocks("") == []

    def test_markdown_blocks_splits_over_limit(self):
        """Content over 3000 chars is split across multiple section blocks."""
        line = "a" * 80 + "\n"
        text = line * 80  # well over 3000
        blocks = markdown_blocks(text)
        assert len(blocks) >= 2
        assert all(
            len(block["text"]["text"]) <= SLACK_SECTION_MRKDWN_MAX_CHARS for block in blocks
        )

    def test_markdown_blocks_max_blocks_truncation_notice(self):
        """When there would be too many blocks, remainder is truncated with a notice."""
        line = "z" * 120 + "\n"
        text = line * 80
        blocks = markdown_blocks(text, max_blocks=2)
        assert len(blocks) == 2
        assert "truncated" in blocks[-1]["text"]["text"].lower()
        assert len(blocks[-1]["text"]["text"]) <= SLACK_SECTION_MRKDWN_MAX_CHARS

    def test_markdown_blocks_max_blocks_zero_clamped(self):
        """max_blocks < 1 is clamped so callers never hit an empty slice / IndexError."""
        blocks = markdown_blocks("hello", max_blocks=0)
        assert len(blocks) == 1
        assert blocks[0]["text"]["text"] == "hello"

    def test_markdown_blocks_converts_markdown_links(self):
        """Markdown links become Slack mrkdwn."""
        blocks = markdown_blocks("[OWASP](https://owasp.org/)")
        assert len(blocks) == 1
        assert "<https://owasp.org/|OWASP>" in blocks[0]["text"]["text"]
