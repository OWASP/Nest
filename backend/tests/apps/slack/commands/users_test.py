from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.users import COMMAND, users_handler


class TestUsersHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
            "text": "test query",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_call_count"),
        [
            (False, 0),
            (True, 1),
        ],
    )
    @patch("apps.slack.commands.users.get_blocks")
    def test_handler_responses(
        self,
        mock_get_blocks,
        commands_enabled,
        expected_call_count,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test blocks"}}]
        mock_get_blocks.return_value = mock_blocks

        users_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        assert mock_get_blocks.call_count == expected_call_count

        if commands_enabled:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            mock_slack_client.chat_postMessage.assert_called_once()

            call_args = mock_slack_client.chat_postMessage.call_args[1]
            assert call_args["blocks"] == mock_blocks
            assert call_args["channel"] == "C123456"
        else:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.commands.users.get_blocks")
    def test_users_handler_with_empty_query(self, mock_get_blocks, mock_slack_client):
        mock_command = {"user_id": "U123456", "text": "  "}
        settings.SLACK_COMMANDS_ENABLED = True

        mock_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test blocks"}}]
        mock_get_blocks.return_value = mock_blocks

        users_handler(ack=MagicMock(), command=mock_command, client=mock_slack_client)

        mock_get_blocks.assert_called_once()
        args, kwargs = mock_get_blocks.call_args
        assert kwargs["search_query"] == ""

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import users

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(users)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "users_handler"
