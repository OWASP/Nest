from unittest.mock import MagicMock

import pytest
from django.test import override_settings

from apps.common.constants import NL, OWASP_URL
from apps.slack.commands.donate import Donate

EXPECTED_BLOCK_COUNT_DONATE = 3


class TestDonateHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_donate_handler(self, mock_client, mock_command):
        ack = MagicMock()
        Donate().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

        mock_client.conversations_open.assert_called_once_with(users="U123456")
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == EXPECTED_BLOCK_COUNT_DONATE

        description_text = blocks[0]["text"]["text"]
        assert "The OWASP Foundation" in description_text
        assert f"{OWASP_URL}/www-policy/operational/donations" in description_text

        assert blocks[1]["type"] == "divider"

        donate_link_text = blocks[2]["text"]["text"]
        expected_link_text = (
            f"{NL}Please Visit <{OWASP_URL}/donate/|OWASP Foundation> page to donate."
        )
        assert donate_link_text == expected_link_text

        assert mock_client.chat_postMessage.call_args[1]["channel"] == "C123456"

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_donate_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        Donate().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_donate_handler_block_structure(self, mock_client, mock_command):
        ack = MagicMock()
        Donate().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == EXPECTED_BLOCK_COUNT_DONATE

        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["type"] == "mrkdwn"
        assert "501(c)(3) non-profit organization" in blocks[0]["text"]["text"]
        assert "OWASP Donations Policy" in blocks[0]["text"]["text"]

        assert blocks[1]["type"] == "divider"

        assert blocks[2]["type"] == "section"
        assert blocks[2]["text"]["type"] == "mrkdwn"
        assert f"{OWASP_URL}/donate/" in blocks[2]["text"]["text"]
