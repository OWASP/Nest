from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.users import users_handler
from apps.slack.common.presentation import EntityPresentation


@pytest.fixture()
def mock_command():
    return {"user_id": "U123456", "text": ""}


@pytest.fixture()
def mock_client():
    client = MagicMock()
    client.conversations_open.return_value = {"channel": {"id": "C123456"}}
    return client


@pytest.mark.parametrize(
    ("commands_enabled", "search_query", "expected_calls"),
    [
        (True, "", 1),
        (True, "test user", 1),
        (False, "", 0),
        (False, "test user", 0),
    ],
)
@patch("apps.slack.commands.users.get_blocks")
def test_users_handler(
    mock_get_blocks, mock_client, mock_command, commands_enabled, search_query, expected_calls
):
    settings.SLACK_COMMANDS_ENABLED = commands_enabled
    mock_command["text"] = search_query
    mock_get_blocks.return_value = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Users"},
        }
    ]

    ack = MagicMock()
    users_handler(ack=ack, command=mock_command, client=mock_client)

    ack.assert_called_once()
    assert mock_client.chat_postMessage.call_count == expected_calls

    if commands_enabled:
        mock_client.conversations_open.assert_called_once_with(users="U123456")
        mock_get_blocks.assert_called_once_with(
            search_query=search_query,
            limit=10,
            presentation=EntityPresentation(
                include_feedback=True,
                include_metadata=True,
                include_pagination=False,
                include_timestamps=True,
                name_truncation=80,
                summary_truncation=300,
            ),
        )
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert blocks == mock_get_blocks.return_value
        assert mock_client.chat_postMessage.call_args[1]["channel"] == "C123456"


@patch("apps.slack.commands.users.get_blocks")
def test_users_handler_with_blocks(mock_get_blocks, mock_client, mock_command):
    settings.SLACK_COMMANDS_ENABLED = True
    mock_get_blocks.return_value = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "User: Test"}},
        {"type": "divider"},
    ]

    ack = MagicMock()
    users_handler(ack=ack, command=mock_command, client=mock_client)

    ack.assert_called_once()
    mock_client.conversations_open.assert_called_once_with(users="U123456")
    blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
    assert len(blocks) == len(mock_get_blocks.return_value)
    assert blocks[0]["text"]["text"] == "User: Test"
    assert blocks[1]["type"] == "divider"
