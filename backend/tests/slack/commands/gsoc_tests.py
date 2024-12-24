import pytest
from unittest.mock import MagicMock, patch
from django.conf import settings
from apps.slack.commands.gsoc import handler, COMMAND
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS
from apps.slack.blocks import markdown


@pytest.fixture
def mock_slack_command():
    return {
        "text": "",
        "user_id": "U123456",
    }


@pytest.fixture
def mock_slack_client():
    client = MagicMock()
    client.conversations_open.return_value = {"channel": {"id": "C123456"}}
    return client


def test_gsoc_handler_with_disabled_commands(mock_slack_client, mock_slack_command):
    settings.SLACK_COMMANDS_ENABLED = False

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    mock_slack_client.conversations_open.assert_not_called()
    mock_slack_client.chat_postMessage.assert_not_called()


@patch('apps.slack.common.gsoc.GSOC_GENERAL_INFORMATION_BLOCKS', new=[markdown("Mocked Info")])
def test_gsoc_handler_with_empty_command_text(mock_slack_client, mock_slack_command):
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]['blocks']
    assert any(f"*`{COMMAND}` is not supported*" in str(block) for block in blocks)


def test_gsoc_handler_with_invalid_command_text(mock_slack_client):
    command = {"text": "invalid", "user_id": "U123456"}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]['blocks']
    assert any(f"*`{COMMAND} invalid` is not supported*" in str(block) for block in blocks)
