from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.jobs import COMMAND, jobs_handler
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_JOBS_CHANNEL_ID

EXPECTED_BLOCK_COUNT_JOBS = 3


class TestJobsHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    def test_handler_disabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = False

        jobs_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    def test_handler_enabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True

        jobs_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert OWASP_JOBS_CHANNEL_ID in text
        assert "Disclaimer" in text
        assert "feedback" in text.lower()

    def test_handler_with_different_user(self, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        custom_command = {"user_id": "U654321", "text": ""}

        jobs_handler(ack=MagicMock(), command=custom_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users="U654321")

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import jobs

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(jobs)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "jobs_handler"

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_calls"),
        [
            (True, 1),
            (False, 0),
        ],
    )
    def test_jobs_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        ack = MagicMock()
        jobs_handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == expected_calls

        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])

            call_args = mock_client.chat_postMessage.call_args[1]
            assert call_args["channel"] == "C123456"

            blocks = call_args["blocks"]
            assert len(blocks) == EXPECTED_BLOCK_COUNT_JOBS

            block1_text = blocks[0]["text"]["text"]
            expected_block1_text = (
                f"Please join <{OWASP_JOBS_CHANNEL_ID}> channel{NL}"
                "This Slack channel shares community-driven job opportunities, networking, "
                "and career advice in cybersecurity and related fields."
            )
            assert block1_text == expected_block1_text

            block2_text = blocks[1]["text"]["text"]
            assert "⚠️ *Disclaimer:" in block2_text

            block3_text = blocks[2]["text"]["text"]
            assert FEEDBACK_CHANNEL_MESSAGE in block3_text
