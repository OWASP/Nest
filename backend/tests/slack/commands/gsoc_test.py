from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.blocks import markdown
from apps.slack.commands.gsoc import COMMAND, gsoc_handler
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE


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
            (False, "", None),
            (True, "", "GSOC_GENERAL_INFORMATION_BLOCKS"),
            (
                True,
                "invalid",
                f"*`{COMMAND} invalid` is not supported*{NL}",
            ),
            (True, "2011", "Year 2011 is not supported. Supported years: 2012-2025"),
        ],
    )
    def test_handler_responses(
        self, commands_enabled, command_text, expected_message, mock_slack_client
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        command = {"text": command_text, "user_id": "U123456"}

        with patch(
            "apps.slack.common.gsoc.GSOC_GENERAL_INFORMATION_BLOCKS",
            new=[markdown("GSOC_GENERAL_INFORMATION_BLOCKS")],
        ):
            gsoc_handler(ack=MagicMock(), command=command, client=mock_slack_client)

            if not commands_enabled:
                mock_slack_client.conversations_open.assert_not_called()
                mock_slack_client.chat_postMessage.assert_not_called()
            else:
                mock_slack_client.conversations_open.assert_called_once_with(
                    users=command["user_id"]
                )
                mock_slack_client.chat_postMessage.assert_called_once()

                blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
                block_texts = [block["text"]["text"] for block in blocks]

                if command_text == "":
                    assert "GSOC_GENERAL_INFORMATION_BLOCKS" in block_texts[0]
                    assert FEEDBACK_CHANNEL_MESSAGE in block_texts[1]
                else:
                    assert any(expected_message in text for text in block_texts)

    def test_handler_with_projects(self, mock_slack_client):
        """Test handler when projects are found for a valid year."""
        mock_projects = [
            {
                "idx_name": "Test Project",
                "idx_url": "https://owasp.org/www-project-bug-logging-tool/",
            }
        ]

        command = {"text": "2024", "user_id": "U123456"}
        settings.SLACK_COMMANDS_ENABLED = True

        with patch(
            "apps.slack.utils.get_gsoc_projects",
            return_value=mock_projects,
        ):
            gsoc_handler(ack=MagicMock(), command=command, client=mock_slack_client)

            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            project_block = str(blocks[0])

            expected_link = "<https://owasp.org/www-project-bug-logging-tool/|Test Project>"
            assert expected_link in project_block
