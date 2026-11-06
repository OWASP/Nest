from unittest.mock import MagicMock

import pytest
from django.test import override_settings

from apps.slack.commands.sponsor import Sponsor


class TestSponsorCommand:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_sponsor_handler(self, mock_client, mock_command):
        ack = MagicMock()
        Sponsor().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == 1
        block_text = blocks[0]["text"]["text"]
        assert block_text == "Coming soon..."

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_sponsor_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        Sponsor().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()
