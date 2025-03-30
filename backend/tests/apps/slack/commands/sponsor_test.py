from unittest.mock import MagicMock

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.sponsor import sponsor_handler


class TestSponsorHandler:
    @pytest.fixture()
    def mock_command(self):
        return {"user_id": "U123456"}

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
    def test_sponsor_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        ack = MagicMock()
        sponsor_handler(ack=ack, command=mock_command, client=mock_client)
        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == expected_calls
        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            assert len(blocks) == 1
            block_text = blocks[0]["text"]["text"]
            expected_text = f"Coming soon...{NL}"
            assert block_text == expected_text
