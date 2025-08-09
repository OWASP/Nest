"""Tests for the ai_create_slack_message_chunks Django management command."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_slack_message_chunks import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_message():
    """Return a mock Message instance."""
    message = Mock()
    message.id = 1
    message.text = "test message"
    return message


class TestAiCreateSlackMessageChunksCommand:
    """Test suite for the ai_create_slack_message_chunks command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Create chunks for Slack messages"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=100,
            help="Number of messages to process in each batch",
        )
        parser.add_argument.assert_any_call(
            "--context",
            action="store_true",
            help="Create only context (skip chunks and embeddings)",
        )
        parser.add_argument.assert_any_call(
            "--chunks",
            action="store_true",
            help="Create only chunks+embeddings (requires existing context)",
        )

    def test_handle_no_options_specified(self, command):
        """Test command with no context or chunks options."""
        command.stdout = MagicMock()
        command.style = MagicMock()

        command.handle(batch_size=100, context=False, chunks=False)

        command.style.ERROR.assert_called_once_with(
            "Please specify either --context or --chunks (or both)"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_handle_chunks_missing_openai_key(self, command):
        """Test command with --chunks flag but no OpenAI key."""
        command.stdout = MagicMock()
        command.style = MagicMock()

        command.handle(batch_size=100, context=False, chunks=True)

    @patch("apps.ai.management.commands.ai_create_slack_message_chunks.Message.objects")
    def test_handle_context_only(self, mock_message_objects, command, mock_message):
        """Test command with --context flag only."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_message])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_message]
        mock_message_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(batch_size=100, context=True, chunks=False)

        command.style.SUCCESS.assert_called()

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_slack_message_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_slack_message_chunks.Message.objects")
    def test_handle_chunks_only(self, mock_message_objects, mock_openai, command, mock_message):
        """Test command with --chunks flag only."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_message])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_message]
        mock_message_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(batch_size=100, context=False, chunks=True)

        command.style.SUCCESS.assert_called()

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_slack_message_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_slack_message_chunks.Message.objects")
    def test_handle_both_context_and_chunks(
        self, mock_message_objects, mock_openai, command, mock_message
    ):
        """Test command with both --context and --chunks flags."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_message])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_message]
        mock_message_objects.filter.return_value = mock_queryset

        with (
            patch.object(command, "process_context_batch", return_value=1),
            patch.object(command, "process_chunks_batch", return_value=1),
        ):
            command.handle(batch_size=100, context=True, chunks=True)

        # Should be called once since it uses elif logic (context takes precedence)
        assert command.style.SUCCESS.call_count == 1

    @patch("apps.ai.management.commands.ai_create_slack_message_chunks.Message.objects")
    def test_handle_no_messages_found(self, mock_message_objects, command):
        """Test command when no messages are found."""
        command.stdout = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_message_objects.all.return_value = mock_queryset

        command.handle(batch_size=100, context=True, chunks=False)

        command.stdout.write.assert_called_with("No messages found to process")
