from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.sponsor import COMMAND, sponsor_handler


class TestSponsorHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        "commands_enabled",
        [False, True],
    )
    def test_handler_responses(
        self,
        commands_enabled,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            mock_slack_client.chat_postMessage.assert_called_once()

            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert len(blocks) == 1
            assert "Coming soon..." in blocks[0]["text"]["text"]

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import sponsor

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(sponsor)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "sponsor_handler"

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_calls"),
        [
            (True, 1),
            (False, 0),
        ],
    )
    def test_sponsor_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        ack = MagicMock()
        sponsor_handler(ack=ack, command=mock_command, client=mock_client)
        ack.assert_called_once()
        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            assert len(blocks) == 1
            block_text = blocks[0]["text"]["text"]
            expected_text = f"Coming soon...{NL}"
            assert block_text == expected_text
