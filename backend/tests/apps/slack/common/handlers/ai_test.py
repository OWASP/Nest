"""Tests for AI handler functionality."""

from unittest.mock import patch

from apps.slack.common.handlers.ai import (
    get_blocks,
    get_default_response,
    get_error_blocks,
    process_ai_query,
)
from apps.slack.utils import format_ai_response_for_slack


class TestAiHandler:
    """Test cases for AI handler functionality."""

    @patch("apps.slack.common.handlers.ai.process_ai_query")
    @patch("apps.slack.common.handlers.ai.markdown_blocks")
    def test_get_blocks_with_successful_response(
        self, mock_markdown_blocks, mock_process_ai_query
    ):
        """Test get_blocks with successful AI response."""
        query = "What is OWASP?"
        ai_response = "OWASP is a security organization..."
        formatted = format_ai_response_for_slack(ai_response)
        expected_blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": formatted},
            }
        ]

        mock_process_ai_query.return_value = ai_response
        mock_markdown_blocks.return_value = expected_blocks

        result = get_blocks(query)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), images=None, channel_id=None, is_app_mention=False
        )
        mock_markdown_blocks.assert_called_once_with(formatted)
        assert result == expected_blocks

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
            query.strip(), images=None, channel_id=None, is_app_mention=False
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
            query.strip(), images=None, channel_id=None, is_app_mention=False
        )
        mock_get_error_blocks.assert_called_once()
        assert result == error_blocks

    @patch("apps.slack.common.handlers.ai.process_ai_query")
    @patch("apps.slack.common.handlers.ai.markdown_blocks")
    def test_get_blocks_with_images(self, mock_markdown_blocks, mock_process_ai_query):
        """Test get_blocks passes images through to process_ai_query."""
        query = "What is in this image?"
        images = ["data:image/png;base64,abc123"]
        ai_response = "The image shows a security dashboard."
        formatted = format_ai_response_for_slack(ai_response)
        expected_blocks = [
            {
                "text": {"type": "mrkdwn", "text": formatted},
                "type": "section",
            }
        ]

        mock_process_ai_query.return_value = ai_response
        mock_markdown_blocks.return_value = expected_blocks

        result = get_blocks(query, images=images)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), images=images, channel_id=None, is_app_mention=False
        )
        assert result == expected_blocks

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_success(self, mock_process_query):
        """Test successful AI query processing."""
        query = "What is OWASP?"
        expected_response = "OWASP is a security organization..."

        mock_process_query.return_value = expected_response

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(
            query, images=None, channel_id=None, is_app_mention=False
        )
        assert result == expected_response

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_failure(self, mock_process_query):
        """Test AI query processing failure returns None."""
        query = "What is OWASP?"

        mock_process_query.side_effect = Exception("AI service error")

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(
            query, images=None, channel_id=None, is_app_mention=False
        )
        assert result is None

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_returns_none(self, mock_process_query):
        """Test AI query processing when process_query returns None."""
        query = "What is OWASP?"

        mock_process_query.return_value = None

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(
            query, images=None, channel_id=None, is_app_mention=False
        )
        assert result is None

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_non_owasp_question(self, mock_process_query):
        """Test AI query processing when question is not OWASP-related."""
        query = "What is the weather today?"

        mock_process_query.return_value = get_default_response()

        result = process_ai_query(query)

        mock_process_query.assert_called_once_with(
            query, images=None, channel_id=None, is_app_mention=False
        )
        assert result == get_default_response()

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_with_images(self, mock_process_query):
        """Test process_ai_query passes images through to process_query."""
        query = "Describe this image"
        images = ["data:image/jpeg;base64,img_data"]
        expected_response = "The image shows..."

        mock_process_query.return_value = expected_response

        result = process_ai_query(query, images=images)

        mock_process_query.assert_called_once_with(
            query, images=images, channel_id=None, is_app_mention=False
        )
        assert result == expected_response

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_with_images_and_channel(self, mock_process_query):
        """Test process_ai_query forwards images along with channel_id and is_app_mention."""
        query = "What is this?"
        images = ["data:image/png;base64,abc"]
        channel_id = "C123456"

        mock_process_query.return_value = "Response"

        process_ai_query(query, images=images, channel_id=channel_id, is_app_mention=True)

        mock_process_query.assert_called_once_with(
            query, images=images, channel_id=channel_id, is_app_mention=True
        )

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_rejects_bare_yes_no(self, mock_process_query):
        """Reject bare YES/NO pipeline output."""
        query = "What is OWASP?"
        mock_process_query.return_value = "YES"
        assert process_ai_query(query) is None
        mock_process_query.return_value = "no"
        assert process_ai_query(query) is None
        mock_process_query.return_value = "No, OWASP is a foundation."
        assert process_ai_query(query) == "No, OWASP is a foundation."

    @patch("apps.ai.flows.process_query")
    def test_process_ai_query_rejects_whitespace_only(self, mock_process_query):
        """Whitespace-only output is None."""
        mock_process_query.return_value = "   \n  "
        assert process_ai_query("q") is None

    @patch("apps.slack.common.handlers.ai.markdown_blocks")
    @patch("apps.slack.common.handlers.ai.get_error_blocks")
    @patch("apps.ai.flows.process_query")
    def test_get_blocks_empty_after_formatting(
        self,
        mock_process_query,
        mock_get_error_blocks,
        mock_markdown_blocks,
    ):
        """Empty after formatting returns error blocks."""
        mock_process_query.return_value = "```\n```"
        err = [{"type": "section", "text": {"type": "mrkdwn", "text": "err"}}]
        mock_get_error_blocks.return_value = err

        result = get_blocks("question")

        assert result == err
        mock_get_error_blocks.assert_called_once()
        mock_markdown_blocks.assert_not_called()

    @patch("apps.slack.common.handlers.ai.markdown_blocks")
    def test_get_error_blocks(self, mock_markdown_blocks):
        """Test error blocks generation."""
        expected_error_message = (
            "⚠️ Unfortunately, I'm unable to answer your question at this time.\n"
            "Please try again later or contact support if the issue persists."
        )
        expected_blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": expected_error_message},
            }
        ]
        mock_markdown_blocks.return_value = expected_blocks

        result = get_error_blocks()

        mock_markdown_blocks.assert_called_once_with(expected_error_message)
        assert result == expected_blocks
