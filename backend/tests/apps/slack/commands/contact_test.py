from unittest.mock import MagicMock

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.contact import Contact


class TestContactHandler:
    @pytest.fixture
    def mock_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture
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
    def test_contact_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        ack = MagicMock()
        Contact().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == expected_calls

        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users="U123456")
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            block_text = blocks[0]["text"]["text"]
            expected_text = f"Please visit <https://owasp.org/contact/|OWASP contact> page{NL}{NL}"
            assert block_text == expected_text
            assert mock_client.chat_postMessage.call_args[1]["channel"] == "C123456"

    def test_contact_handler_block_structure(self, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        ack = MagicMock()
        Contact().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == 2
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["type"] == "mrkdwn"
        assert "https://owasp.org/contact/" in blocks[0]["text"]["text"]
        assert blocks[1]["type"] == "section"
        assert blocks[1]["text"]["type"] == "mrkdwn"
        assert "💬 You can share feedback" in blocks[1]["text"]["text"]
