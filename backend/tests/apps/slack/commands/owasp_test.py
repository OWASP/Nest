from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.owasp import Owasp


class TestOwaspHandler:
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

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_help"),
        [
            (True, "", True),
            (True, "-h", True),
            (True, "invalid_command", False),
            (False, "", False),
        ],
    )
    def test_owasp_handler(
        self, mock_client, mock_command, commands_enabled, command_text, expected_help
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = command_text
        ack = MagicMock()
        owasp = Owasp()
        owasp.handler(ack=ack, command=mock_command, client=mock_client)
        if commands_enabled:
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            if expected_help:
                assert any("chapters" in str(block) for block in blocks)
                assert any("committees" in str(block) for block in blocks)
                assert any("projects" in str(block) for block in blocks)
            elif "invalid_command" in command_text:
                assert any("is not supported" in str(block) for block in blocks)
        else:
            mock_client.chat_postMessage.assert_not_called()

    @pytest.mark.parametrize(
        "subcommand", ["chapters", "committees", "contribute", "gsoc", "leaders", "projects"]
    )
    def test_owasp_subcommands(self, subcommand, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = f"{subcommand} test"
        with patch.object(Owasp, "find_command") as mock_find_command:
            mock_find_command.return_value = MagicMock(
                handler=lambda _, command, client: client.chat_postMessage(
                    channel=client.conversations_open(users=command["user_id"])["channel"]["id"],
                    blocks=[
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": f"{subcommand} called"},
                        }
                    ],
                )
            )

            ack = MagicMock()
            owasp = Owasp()
            owasp.handler(ack=ack, command=mock_command, client=mock_client)

            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            assert blocks[0]["text"]["text"] == f"{subcommand} called"
