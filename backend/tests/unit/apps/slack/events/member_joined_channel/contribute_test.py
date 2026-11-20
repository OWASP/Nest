from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from apps.slack.constants import (
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.member_joined_channel.contribute import Contribute


class TestContributeEventHandler:
    @pytest.fixture
    def mock_slack_event(self):
        return {"user": "U123456", "channel": OWASP_CONTRIBUTE_CHANNEL_ID.replace("#", "")}

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @override_settings(SLACK_EVENTS_ENABLED=True)
    @patch("apps.owasp.models.project.Project.active_projects_count")
    @patch("apps.github.models.issue.Issue.open_issues_count")
    @patch("apps.common.utils.get_absolute_url", return_value="/contribute")
    def test_handler_responses(
        self,
        mock_get_absolute_url,
        mock_open_issues_count,
        mock_active_projects_count,
        mock_slack_event,
        mock_slack_client,
    ):
        expected_messages = [
            "20 active OWASP projects",
            "50 recently opened issues",
            NEST_BOT_NAME,
            "/contribute",
            "You can share feedback on your NestBot experience",
        ]
        mock_active_projects_count.return_value = 20
        mock_open_issues_count.return_value = 50

        contribute = Contribute()
        contribute.handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

        # Check that ephemeral message was sent
        mock_slack_client.chat_postEphemeral.assert_called_once()
        ephemeral_call_args = mock_slack_client.chat_postEphemeral.call_args
        assert ephemeral_call_args[1]["channel"] == mock_slack_event["channel"]
        assert ephemeral_call_args[1]["user"] == mock_slack_event["user"]

        # Check that direct message was sent
        mock_slack_client.conversations_open.assert_called_once_with(users="U123456")

        _, kwargs = mock_slack_client.chat_postMessage.call_args
        blocks = kwargs["blocks"]
        block_texts = []
        for block in blocks:
            if block.get("type") == "section":
                text = block.get("text", {}).get("text", "")
                block_texts.append(text)
        combined_text = " ".join(block_texts)

        for message in expected_messages:
            assert message in combined_text

        # The mocks are called twice - once for direct message, once for ephemeral message
        assert mock_active_projects_count.call_count == 2
        assert mock_open_issues_count.call_count == 2

    @override_settings(SLACK_EVENTS_ENABLED=False)
    def test_handler_when_events_disabled(self, mock_slack_event, mock_slack_client):
        contribute = Contribute()
        contribute.handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

        mock_slack_client.chat_postEphemeral.assert_not_called()
        mock_slack_client.conversations_open.assert_not_called()
        mock_slack_client.chat_postMessage.assert_not_called()

    @pytest.mark.parametrize(
        ("channel_id", "expected_result"),
        [
            (OWASP_CONTRIBUTE_CHANNEL_ID.replace("#", ""), True),
            ("C999999", False),
        ],
    )
    def test_matcher(self, channel_id, expected_result):
        contribute = Contribute()
        assert contribute.matchers[0]({"channel": channel_id}) == expected_result
