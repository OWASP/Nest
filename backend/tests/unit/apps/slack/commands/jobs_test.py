from unittest.mock import MagicMock

import pytest
from django.test import override_settings

from apps.common.constants import NL
from apps.slack.commands.jobs import Jobs
from apps.slack.constants import FEEDBACK_SHARING_INVITE, OWASP_JOBS_CHANNEL_ID

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

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_jobs_handler(self, mock_client, mock_command):
        ack = MagicMock()
        Jobs().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        call_args = mock_client.chat_postMessage.call_args[1]
        assert call_args["channel"] == "C123456"

        blocks = call_args["blocks"]
        assert len(blocks) == EXPECTED_BLOCK_COUNT_JOBS

        block1_text = blocks[0]["text"]["text"]
        expected_block1_text = (
            f"Please join <{OWASP_JOBS_CHANNEL_ID}> channel{NL}"
            "This Slack channel shares community-driven job opportunities, networking, "
            f"and career advice in cybersecurity and related fields.{NL}{NL}"
        )
        assert block1_text == expected_block1_text

        block2_text = blocks[1]["text"]["text"]
        assert "⚠️ *Disclaimer:" in block2_text

        block3_text = blocks[2]["text"]["text"]
        assert FEEDBACK_SHARING_INVITE.strip() in block3_text

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_jobs_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        Jobs().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()
