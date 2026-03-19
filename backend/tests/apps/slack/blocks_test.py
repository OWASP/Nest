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
        """Long AI answers must still produce ≤3000 chars per section (Slack invalid_blocks)."""
        blocks = markdown_blocks("Hello OWASP")
        assert len(blocks) == 1
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["text"] == "Hello OWASP"

    def test_markdown_blocks_empty_input(self):
        """Empty string yields no blocks (callers should avoid posting empty-only)."""
        assert markdown_blocks("") == []

    def test_markdown_blocks_splits_over_limit(self):
        """Content over 3000 chars is split across multiple section blocks."""
        line = "a" * 80 + "\n"
        text = line * 80  # well over 3000
        blocks = markdown_blocks(text)
        assert len(blocks) >= 2
        for block in blocks:
            assert len(block["text"]["text"]) <= SLACK_SECTION_MRKDWN_MAX_CHARS

    def test_markdown_blocks_max_blocks_truncation_notice(self):
        """When there would be too many blocks, remainder is truncated with a notice."""
        line = "z" * 120 + "\n"
        text = line * 80
        blocks = markdown_blocks(text, max_blocks=2)
        assert len(blocks) == 2
        assert "truncated" in blocks[-1]["text"]["text"].lower()
