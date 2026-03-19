"""Tests for AI handler functionality."""

from unittest.mock import patch

from apps.slack.common.handlers.ai import (
    MAX_BLOCK_TEXT_LENGTH,
    format_blocks,
    get_blocks,
    get_default_response,
    get_error_blocks,
    process_ai_query,
)


class TestAiHandler:
    """Test cases for AI handler functionality."""

    @patch("apps.slack.common.handlers.ai.process_ai_query")
    @patch("apps.slack.common.handlers.ai.format_blocks")
    def test_get_blocks_with_successful_response(self, mock_format_blocks, mock_process_ai_query):
        """Test get_blocks with successful AI response."""
        query = "What is OWASP?"
        ai_response = "OWASP is a security organization..."
        expected_block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ai_response},
        }

        mock_process_ai_query.return_value = ai_response
        mock_format_blocks.return_value = [expected_block]

        result = get_blocks(query)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), images=None, channel_id=None, is_app_mention=False
        )
        mock_format_blocks.assert_called_once_with(ai_response)
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
    @patch("apps.slack.common.handlers.ai.format_blocks")
    def test_get_blocks_with_images(self, mock_format_blocks, mock_process_ai_query):
        """Test get_blocks passes images through to process_ai_query."""
        query = "What is in this image?"
        images = ["data:image/png;base64,abc123"]
        ai_response = "The image shows a security dashboard."
        expected_block = {
            "text": {"type": "mrkdwn", "text": ai_response},
            "type": "section",
        }

        mock_process_ai_query.return_value = ai_response
        mock_format_blocks.return_value = [expected_block]

        result = get_blocks(query, images=images)

        mock_process_ai_query.assert_called_once_with(
            query.strip(), images=images, channel_id=None, is_app_mention=False
        )
        assert result == [expected_block]

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
    def test_process_ai_query_rejects_yes_no(self, mock_process_query):
        """Bare YES/NO from the model must not be returned to callers."""
        mock_process_query.return_value = "YES"
        assert process_ai_query("anything") is None
        mock_process_query.return_value = "NO"
        assert process_ai_query("anything") is None
        mock_process_query.return_value = "  no  "
        assert process_ai_query("anything") is None

    def test_format_blocks_splits_long_text(self):
        """Long answers become multiple Slack blocks under the size limit."""
        chunk = "a" * MAX_BLOCK_TEXT_LENGTH
        remainder = "tail"
        text = f"{chunk}\n{remainder}"
        blocks = format_blocks(text)
        assert len(blocks) >= 2
        for block in blocks:
            block_text = block["text"]["text"]
            assert len(block_text) <= 3001  # Slack mrkdwn section limit

    def test_format_blocks_single_short_message(self):
        """Short text becomes one markdown block with link conversion."""
        text = "See [OWASP](https://owasp.org)"
        blocks = format_blocks(text)
        assert len(blocks) == 1
        assert "<https://owasp.org|OWASP>" in blocks[0]["text"]["text"]

    @patch("apps.slack.common.handlers.ai.get_error_blocks")
    def test_format_blocks_empty_uses_error_blocks(self, mock_error):
        """Whitespace-only / empty content should not produce an empty block list."""
        err = [{"type": "section", "text": {"type": "mrkdwn", "text": "err"}}]
        mock_error.return_value = err
        assert format_blocks("") == err
        assert format_blocks("   \n\t  ") == err
        assert mock_error.call_count == 2

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
