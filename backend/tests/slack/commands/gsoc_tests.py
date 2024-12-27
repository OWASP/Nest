from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.blocks import markdown
from apps.slack.commands.gsoc import COMMAND, handler


class TestGsocHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_message"),
        [
            (False, "", None),  # Disabled commands case
            (True, "", f"*`{COMMAND}` is not supported*"),  # Empty text case
            (True, "invalid", f"*`{COMMAND} invalid` is not supported*"),  # Invalid text case
        ],
    )
    def test_handler_responses(
        self, commands_enabled, command_text, expected_message, mock_slack_client
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        command = {"text": command_text, "user_id": "U123456"}

        with patch(
            "apps.slack.common.gsoc.GSOC_GENERAL_INFORMATION_BLOCKS", new=[markdown("Mocked Info")]
        ):
            handler(ack=MagicMock(), command=command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert any(expected_message in str(block) for block in blocks)
