from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.donate import COMMAND, donate_handler

EXPECTED_BLOCK_COUNT_DONATE = 3


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

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_calls"),
        [
            (True, 1),
            (False, 0),
        ],
    )
    def test_donate_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        ack = MagicMock()
        donate_handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        assert mock_client.chat_postMessage.call_count == expected_calls

        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users="U123456")
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            assert len(blocks) == EXPECTED_BLOCK_COUNT_DONATE

            description_text = blocks[0]["text"]["text"]
            assert "The OWASP Foundation" in description_text
            assert (
                f"https://{OWASP_WEBSITE_URL}/www-policy/operational/donations" in description_text
            )

            assert blocks[1]["type"] == "divider"

            donate_link_text = blocks[2]["text"]["text"]
            expected_link_text = (
                f"Please Visit <{OWASP_WEBSITE_URL}/donate/| OWASP Foundation> page to donate."
            )
            assert donate_link_text == expected_link_text

            assert mock_client.chat_postMessage.call_args[1]["channel"] == "C123456"

    def test_donate_handler_block_structure(self, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True

        ack = MagicMock()
        donate_handler(ack=ack, command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == EXPECTED_BLOCK_COUNT_DONATE

        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["type"] == "mrkdwn"
        assert "501(c)(3) nonprofit organization" in blocks[0]["text"]["text"]
        assert "OWASP Donations Policy" in blocks[0]["text"]["text"]

        assert blocks[1]["type"] == "divider"

        assert blocks[2]["type"] == "section"
        assert blocks[2]["text"]["type"] == "mrkdwn"
        assert f"{OWASP_WEBSITE_URL}/donate/" in blocks[2]["text"]["text"]
