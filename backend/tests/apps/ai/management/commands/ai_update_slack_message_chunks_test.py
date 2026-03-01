from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_update_slack_message_chunks import Command
from apps.slack.models.message import Message


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_message():
    message = Mock()
    message.id = 1
    message.slack_message_id = "test-message-id"
    return message


class TestAiCreateSlackMessageChunksCommand:
    def test_command_inheritance(self, command):
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        assert command.model_class == Message

    def test_entity_name_property(self, command):
        assert command.entity_name == "message"

    def test_entity_name_plural_property(self, command):
        assert command.entity_name_plural == "messages"

    def test_key_field_name_property(self, command):
        assert command.key_field_name == "slack_message_id"

    def test_source_name_property(self, command):
        """Test the source_name property."""
        assert command.source_name() == "slack_message"

    def test_extract_content(self, command, mock_message):
        """Test the extract_content method."""
        mock_message.cleaned_text = "Test message content"
        content = command.extract_content(mock_message)
        assert content == ("Test message content", "")

    def test_extract_content_none_cleaned_text(self, command, mock_message):
        """Test the extract_content method with None cleaned_text."""
        mock_message.cleaned_text = None
        content = command.extract_content(mock_message)
        assert content == ("", "")

    def test_get_default_queryset(self, command):
        """Test the get_default_queryset method."""
        with patch.object(command, "get_base_queryset") as mock_base:
            mock_base.return_value = Mock()
            result = command.get_default_queryset()
            mock_base.assert_called_once()
            assert result == mock_base.return_value

    def test_add_arguments(self, command):
        """Test the add_arguments method."""
        parser = Mock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 3
        calls = parser.add_argument.call_args_list

        assert calls[0][0] == ("--message-key",)
        assert calls[0][1]["type"] is str
        assert "Process only the message with this key" in calls[0][1]["help"]

        assert calls[1][0] == ("--all",)
        assert calls[1][1]["action"] == "store_true"
        assert "Process all the messages" in calls[1][1]["help"]

        assert calls[2][0] == ("--batch-size",)
        assert calls[2][1]["type"] is int
        assert calls[2][1]["default"] == 100
        assert "Number of messages to process in each batch" in calls[2][1]["help"]
