from unittest.mock import MagicMock, Mock

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_slack_message_context import Command


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_message():
    message = Mock()
    message.id = 1
    message.pk = 1
    message.slack_message_id = "test-message-123"
    message.cleaned_text = "This is a test Slack message content."
    return message


class TestAiCreateSlackMessageContextCommand:
    def test_command_inheritance(self, command):
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        from apps.slack.models.message import Message

        assert command.model_class == Message

    def test_entity_name_property(self, command):
        assert command.entity_name == "message"

    def test_entity_name_plural_property(self, command):
        assert command.entity_name_plural == "messages"

    def test_key_field_name_property(self, command):
        assert command.key_field_name == "slack_message_id"

    def test_source_name_property(self, command):
        assert command.source_name == "slack_message"

    def test_extract_content(self, command, mock_message):
        content = command.extract_content(mock_message)
        assert content == ("This is a test Slack message content.", "")

    def test_extract_content_empty_text(self, command):
        message = Mock()
        message.cleaned_text = None
        content = command.extract_content(message)
        assert content == ("", "")

    def test_add_arguments(self, command):
        parser = MagicMock()
        command.add_arguments(parser)
        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call(
            "--message-key",
            type=str,
            help="Process only the message with this key",
        )
        parser.add_argument.assert_any_call(
            "--all",
            action="store_true",
            help="Process all the messages",
        )
        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=100,
            help="Number of messages to process in each batch",
        )
