from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.board import COMMAND, board_handler


class TestBoardHandler:
    @pytest.fixture()
    def mock_command(self):
        return {"text": "", "user_id": "U123456"}

    @pytest.fixture()
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_calls"),
        [
            (True, 1),
            (False, 0),
        ],
    )
    def test_board_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        board_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        assert mock_client.chat_postMessage.call_count == expected_calls

        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users="U123456")
            mock_client.chat_postMessage.assert_called_once()

            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            channel = mock_client.chat_postMessage.call_args[1]["channel"]

            assert channel == "C123456"
            assert any("Global board" in str(block) for block in blocks)

    def test_command_registration(self):
        with patch("apps.slack.apps.SlackConfig.app") as mock_app:
            mock_command_decorator = MagicMock()
            mock_app.command.return_value = mock_command_decorator

            import importlib

            import apps.slack.commands.board

            importlib.reload(apps.slack.commands.board)

            mock_app.command.assert_called_once_with(COMMAND)
            assert mock_command_decorator.call_count == 1
