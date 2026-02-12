"""Tests for AI handler functionality."""

from unittest.mock import patch

from apps.slack.common.handlers.ai import (
    get_blocks,
    get_default_response,
    get_error_blocks,
    process_ai_query,
)


class TestAiHandler:
    """Test cases for AI handler functionality."""

    @patch("apps.slack.common.handlers.ai.process_ai_query")
    @patch("apps.slack.common.handlers.ai.markdown")
    def test_get_blocks_with_successful_response(self, mock_markdown, mock_process_ai_query):
        """Test get_blocks with successful AI response."""
        query = "What is OWASP?"
        ai_response = "OWASP is a security organization..."
        expected_block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ai_response},
        }

        mock_process_ai_query.return_value = ai_response
        mock_markdown.return_value = expected_block

        result = get_blocks(query)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), channel_id=None, is_app_mention=False
        )
        mock_markdown.assert_called_once_with(ai_response)
        assert result == [expected_block]

    @patch("apps.slack.common.handlers.ai.process_ai_query")
    @patch("apps.slack.common.handlers.ai.get_error_blocks")
    def test_get_blocks_with_no_response(self, mock_get_error_blocks, mock_process_ai_query):
        """Test get_blocks when AI returns no response."""
        query = "What is OWASP?"
        error_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Error message"}}]

        mock_process_ai_query.return_value = None
        mock_get_error_blocks.return_value = error_blocks

        result = get_blocks(query)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), channel_id=None, is_app_mention=False
        )
        mock_get_error_blocks.assert_called_once()
        assert result == error_blocks

    @patch("apps.slack.common.handlers.ai.process_ai_query")
    @patch("apps.slack.common.handlers.ai.get_error_blocks")
    def test_get_blocks_with_empty_response(self, mock_get_error_blocks, mock_process_ai_query):
        """Test get_blocks when AI returns empty response."""
        query = "What is OWASP?"
        error_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Error message"}}]

        mock_process_ai_query.return_value = ""
        mock_get_error_blocks.return_value = error_blocks

        result = get_blocks(query)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), channel_id=None, is_app_mention=False
        )
        mock_get_error_blocks.assert_called_once()
        assert result == error_blocks

    @patch("apps.slack.common.handlers.ai.process_query")
    def test_process_ai_query_success(self, mock_process_query):
        """Test successful AI query processing."""
        query = "What is OWASP?"
        expected_response = "OWASP is a security organization..."

        mock_process_query.return_value = expected_response

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(query, channel_id=None, is_app_mention=False)
        assert result == expected_response

    @patch("apps.slack.common.handlers.ai.process_query")
    def test_process_ai_query_failure(self, mock_process_query):
        """Test AI query processing failure returns None."""
        query = "What is OWASP?"

        mock_process_query.side_effect = Exception("AI service error")

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(query, channel_id=None, is_app_mention=False)
        assert result is None

    @patch("apps.slack.common.handlers.ai.process_query")
    def test_process_ai_query_returns_none(self, mock_process_query):
        """Test AI query processing when process_query returns None."""
        query = "What is OWASP?"

        mock_process_query.return_value = None

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(query, channel_id=None, is_app_mention=False)
        assert result is None

    @patch("apps.slack.common.handlers.ai.process_query")
    def test_process_ai_query_non_owasp_question(self, mock_process_query):
        """Test AI query processing when question is not OWASP-related."""
        query = "What is the weather today?"

        mock_process_query.return_value = get_default_response()

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(query, channel_id=None, is_app_mention=False)
        assert result == get_default_response()

    @patch("apps.slack.common.handlers.ai.markdown")
    def test_get_error_blocks(self, mock_markdown):
        """Test error blocks generation."""
        expected_error_message = (
            "⚠️ Unfortunately, I'm unable to answer your question at this time.\n"
            "Please try again later or contact support if the issue persists."
        )
        expected_block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": expected_error_message},
        }
        mock_markdown.return_value = expected_block

        result = get_error_blocks()

        mock_markdown.assert_called_once_with(expected_error_message)
        assert result == [expected_block]

    def test_get_blocks_strips_whitespace(self):
        """Test that get_blocks properly strips whitespace from query."""
        with patch("apps.slack.common.handlers.ai.process_ai_query") as mock_process_ai_query:
            mock_process_ai_query.return_value = None
            with patch("apps.slack.common.handlers.ai.get_error_blocks") as mock_get_error_blocks:
                mock_get_error_blocks.return_value = []

                query_with_whitespace = "  What is OWASP?  "
                get_blocks(query_with_whitespace)

                mock_process_ai_query.assert_called_once_with(
                    "What is OWASP?", channel_id=None, is_app_mention=False
                )
