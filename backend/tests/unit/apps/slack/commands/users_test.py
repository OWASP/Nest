from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from apps.slack.commands.users import Users
from apps.slack.common.presentation import EntityPresentation


class TestUsersHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456", "text": ""}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize("search_query", ["", "test user"])
    @patch("apps.slack.commands.users.get_blocks")
    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_users_handler(self, mock_get_blocks, mock_client, mock_command, search_query):
        mock_command["text"] = search_query
        mock_get_blocks.return_value = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Users"},
            }
        ]

        ack = MagicMock()
        Users().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

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

    @pytest.mark.parametrize("search_query", ["", "test user"])
    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_users_handler_when_commands_disabled(self, mock_client, mock_command, search_query):
        mock_command["text"] = search_query
        ack = MagicMock()
        Users().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.commands.users.get_blocks")
    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_users_handler_with_blocks(self, mock_get_blocks, mock_client, mock_command):
        mock_get_blocks.return_value = [
            {"type": "section", "text": {"type": "mrkdwn", "text": "User: Test"}},
            {"type": "divider"},
        ]

        ack = MagicMock()
        Users().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        mock_client.conversations_open.assert_called_once_with(users="U123456")
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == len(mock_get_blocks.return_value)
        assert blocks[0]["text"]["text"] == "User: Test"
        assert blocks[1]["type"] == "divider"
