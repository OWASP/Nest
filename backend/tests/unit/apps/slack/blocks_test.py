"""Tests for Slack blocks."""

from apps.slack.blocks import divider, markdown


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
