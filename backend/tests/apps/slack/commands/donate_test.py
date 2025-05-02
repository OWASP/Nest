from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.donate import COMMAND, donate_handler


class TestDonateHandler:
    @pytest.fixture
    def mock_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    def test_handler_disabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = False

        donate_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    def test_handler_enabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True

        donate_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "OWASP Foundation" in text
        assert "501(c)(3) nonprofit" in text
        assert OWASP_WEBSITE_URL in text
        assert "donate" in text.lower()

    def test_handler_with_different_user(self, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        custom_command = {"user_id": "U654321", "text": ""}

        donate_handler(ack=MagicMock(), command=custom_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users="U654321")

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import donate

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(donate)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "donate_handler"
