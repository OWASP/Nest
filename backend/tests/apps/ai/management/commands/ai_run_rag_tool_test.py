"""Tests for the ai_run_rag_tool Django management command."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_run_rag_tool import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


class TestAiRunRagToolCommand:
    """Test suite for the ai_run_rag_tool command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Test the RagTool functionality with a sample query"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 6
        parser.add_argument.assert_any_call(
            "--query",
            type=str,
            default="What is OWASP Foundation?",
            help="Query to test the Rag tool",
        )
        parser.add_argument.assert_any_call(
            "--limit",
            type=int,
            default=8,  # DEFAULT_CHUNKS_RETRIEVAL_LIMIT
            help="Maximum number of results to retrieve",
        )
        parser.add_argument.assert_any_call(
            "--threshold",
            type=float,
            default=0.1,  # DEFAULT_SIMILARITY_THRESHOLD
            help="Similarity threshold (0.0 to 1.0)",
        )
        parser.add_argument.assert_any_call(
            "--content-types",
            nargs="+",
            default=None,
            help="Content types to filter by (e.g., project chapter)",
        )
        parser.add_argument.assert_any_call(
            "--embedding-model",
            type=str,
            default="text-embedding-3-small",
            help="OpenAI embedding model",
        )
        parser.add_argument.assert_any_call(
            "--chat-model",
            type=str,
            default="gpt-4o",
            help="OpenAI chat model",
        )

    @patch("apps.ai.management.commands.ai_run_rag_tool.RagTool")
    def test_handle_success(self, mock_rag_tool, command):
        """Test successful command execution."""
        command.stdout = MagicMock()
        mock_rag_instance = MagicMock()
        mock_rag_instance.query.return_value = "Test answer"
        mock_rag_tool.return_value = mock_rag_instance

        command.handle(
            query="Test query",
            limit=10,
            threshold=0.8,
            content_types=["project", "chapter"],
            embedding_model="text-embedding-3-small",
            chat_model="gpt-4o",
        )

        mock_rag_tool.assert_called_once_with(
            chat_model="gpt-4o", embedding_model="text-embedding-3-small"
        )
        mock_rag_instance.query.assert_called_once_with(
            content_types=["project", "chapter"],
            limit=10,
            question="Test query",
            similarity_threshold=0.8,
        )
        command.stdout.write.assert_any_call("\nProcessing query...")
        command.stdout.write.assert_any_call("\nAnswer: Test answer")

    @patch("apps.ai.management.commands.ai_run_rag_tool.RagTool")
    def test_handle_initialization_error(self, mock_rag_tool, command):
        """Test command when RagTool initialization fails."""
        command.stderr = MagicMock()
        command.style = MagicMock()
        mock_rag_tool.side_effect = ValueError("Initialization error")

        command.handle(
            query="What is OWASP Foundation?",
            limit=8,
            threshold=0.1,
            content_types=None,
            embedding_model="text-embedding-3-small",
            chat_model="gpt-4o",
        )
        command.stderr.write.assert_called_once()

    @patch("apps.ai.management.commands.ai_run_rag_tool.RagTool")
    def test_handle_with_default_values(self, mock_rag_tool, command):
        """Test command with default argument values."""
        command.stdout = MagicMock()
        mock_rag_instance = MagicMock()
        mock_rag_instance.query.return_value = "Default answer"
        mock_rag_tool.return_value = mock_rag_instance

        command.handle(
            query="What is OWASP Foundation?",
            limit=8,
            threshold=0.1,
            content_types=None,
            embedding_model="text-embedding-3-small",
            chat_model="gpt-4o",
        )

        mock_rag_tool.assert_called_once_with(
            chat_model="gpt-4o", embedding_model="text-embedding-3-small"
        )
        mock_rag_instance.query.assert_called_once_with(
            content_types=None,
            limit=8,  # DEFAULT_CHUNKS_RETRIEVAL_LIMIT
            question="What is OWASP Foundation?",
            similarity_threshold=0.1,  # DEFAULT_SIMILARITY_THRESHOLD
        )
