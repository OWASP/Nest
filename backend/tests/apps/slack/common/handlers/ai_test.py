"""Tests for AI handler functionality."""

from unittest.mock import Mock, patch

import pytest

from apps.slack.common.handlers.ai import get_blocks, get_error_blocks, process_ai_query


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

        mock_process_ai_query.assert_called_once_with(query.strip())
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

        mock_process_ai_query.assert_called_once_with(query.strip())
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

        mock_process_ai_query.assert_called_once_with(query.strip())
        mock_get_error_blocks.assert_called_once()
        assert result == error_blocks

    @patch("apps.slack.common.handlers.ai.RagTool")
    def test_process_ai_query_success(self, mock_rag_tool):
        """Test successful AI query processing."""
        query = "What is OWASP?"
        expected_response = "OWASP is a security organization..."

        mock_rag_instance = Mock()
        mock_rag_instance.query.return_value = expected_response
        mock_rag_tool.return_value = mock_rag_instance

        result = process_ai_query(query)

        mock_rag_tool.assert_called_once_with(
            chat_model="gpt-4o",
            embedding_model="text-embedding-3-small",
        )
        mock_rag_instance.query.assert_called_once_with(question=query)
        assert result == expected_response

    @patch("apps.slack.common.handlers.ai.RagTool")
    def test_process_ai_query_failure(self, mock_rag_tool):
        """Test AI query processing failure."""
        query = "What is OWASP?"

        mock_rag_instance = Mock()
        mock_rag_instance.query.side_effect = Exception("AI service error")
        mock_rag_tool.return_value = mock_rag_instance

        with pytest.raises(Exception, match="AI service error"):
            process_ai_query(query)

    @patch("apps.slack.common.handlers.ai.RagTool")
    def test_process_ai_query_returns_none(self, mock_rag_tool):
        """Test AI query processing when RAG tool returns None."""
        query = "What is OWASP?"

        mock_rag_instance = Mock()
        mock_rag_instance.query.return_value = None
        mock_rag_tool.return_value = mock_rag_instance

        result = process_ai_query(query)

        mock_rag_tool.assert_called_once_with(
            chat_model="gpt-4o",
            embedding_model="text-embedding-3-small",
        )
        mock_rag_instance.query.assert_called_once_with(question=query)
        assert result is None

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

                mock_process_ai_query.assert_called_once_with("What is OWASP?")
