from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.blocks import markdown
from apps.slack.commands.gsoc import Gsoc
from apps.slack.constants import FEEDBACK_SHARING_INVITE


class TestGsocCommand:
    @pytest.fixture
    def mock_slack_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture
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
                "*`/gsoc invalid` is not supported",
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
            ack = MagicMock()
            Gsoc().handler(ack=ack, command=command, client=mock_slack_client)

            ack.assert_called_once()

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
                    assert "Getting Started with OWASP GSoC" in block_texts[0]
                    assert any(FEEDBACK_SHARING_INVITE in text for text in block_texts)
                else:
                    assert any(expected_message in text for text in block_texts)

    def test_handler_with_projects(self, mock_slack_client):
        mock_projects = [
            {
                "name": "Test Project",
                "url": "https://owasp.org/www-project-bug-logging-tool/",
            }
        ]
        command = {"text": "2024", "user_id": "U123456"}
        settings.SLACK_COMMANDS_ENABLED = True
        with patch(
            "apps.owasp.utils.gsoc.get_gsoc_projects",
            return_value=mock_projects,
        ):
            ack = MagicMock()
            Gsoc().handler(ack=ack, command=command, client=mock_slack_client)

            ack.assert_called_once()

            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            project_block = str(blocks[0])

            assert (
                "<https://owasp.org/www-project-bug-logging-tool/|Test Project>" in project_block
            )
