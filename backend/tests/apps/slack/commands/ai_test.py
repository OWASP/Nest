"""Tests for AI command functionality."""

from unittest.mock import patch

import pytest

from apps.slack.commands.ai import Ai


class TestAiCommand:
    """Test cases for AI command functionality."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test data before each test method."""
        self.ai_command = Ai()

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_success(self, mock_get_blocks):
        """Test successful rendering of AI response blocks."""
        command = {
            "text": "What is OWASP?",
            "user_id": "U123456",
            "channel_id": "C123456",
        }
        expected_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "OWASP is a security organization...",
                },
            }
        ]
        mock_get_blocks.return_value = expected_blocks

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(query="What is OWASP?")
        assert result == expected_blocks

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_with_whitespace(self, mock_get_blocks):
        """Test rendering blocks with text that has whitespace."""
        command = {
            "text": "  What is OWASP security?  ",
            "user_id": "U123456",
            "channel_id": "C123456",
        }
        expected_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "OWASP is a security organization...",
                },
            }
        ]
        mock_get_blocks.return_value = expected_blocks

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(query="What is OWASP security?")
        assert result == expected_blocks

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_empty_text(self, mock_get_blocks):
        """Test rendering blocks with empty text."""
        command = {"text": "", "user_id": "U123456", "channel_id": "C123456"}
        expected_blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": "Error message"}}
        ]
        mock_get_blocks.return_value = expected_blocks

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(query="")
        assert result == expected_blocks

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_only_whitespace(self, mock_get_blocks):
        """Test rendering blocks with only whitespace in text."""
        command = {"text": "   ", "user_id": "U123456", "channel_id": "C123456"}
        expected_blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": "Error message"}}
        ]
        mock_get_blocks.return_value = expected_blocks

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(query="")
        assert result == expected_blocks

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_complex_query(self, mock_get_blocks):
        """Test rendering blocks with complex query."""
        command = {
            "text": "What are the OWASP Top 10 vulnerabilities and how can I prevent them?",
            "user_id": "U123456",
            "channel_id": "C123456",
        }
        expected_blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "The OWASP Top 10 is a list..."},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Prevention techniques..."},
            },
        ]
        mock_get_blocks.return_value = expected_blocks

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(
            query="What are the OWASP Top 10 vulnerabilities and how can I prevent them?"
        )
        assert result == expected_blocks

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_handles_exception(self, mock_get_blocks):
        """Test that render_blocks handles exceptions gracefully."""
        command = {
            "text": "What is OWASP?",
            "user_id": "U123456",
            "channel_id": "C123456",
        }
        mock_get_blocks.side_effect = Exception("AI service error")

        ai_command = Ai()
        with pytest.raises(Exception, match="AI service error"):
            ai_command.render_blocks(command)

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_returns_none(self, mock_get_blocks):
        """Test handling when get_blocks returns None."""
        command = {
            "text": "What is OWASP?",
            "user_id": "U123456",
            "channel_id": "C123456",
        }
        mock_get_blocks.return_value = None

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(query="What is OWASP?")
        assert result is None

    def test_ai_command_inheritance(self):
        """Test that Ai command inherits from CommandBase."""
        from apps.slack.commands.command import CommandBase

        ai_command = Ai()
        assert isinstance(ai_command, CommandBase)

    @patch("apps.slack.common.handlers.ai.get_blocks")
    def test_render_blocks_special_characters(self, mock_get_blocks):
        """Test rendering blocks with special characters in query."""
        command = {
            "text": "What is XSS & SQL injection? How to prevent <script> attacks?",
            "user_id": "U123456",
            "channel_id": "C123456",
        }
        expected_blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "XSS and SQL injection..."},
            }
        ]
        mock_get_blocks.return_value = expected_blocks

        ai_command = Ai()
        result = ai_command.render_blocks(command)

        mock_get_blocks.assert_called_once_with(
            query="What is XSS & SQL injection? How to prevent <script> attacks?"
        )
        assert result == expected_blocks
