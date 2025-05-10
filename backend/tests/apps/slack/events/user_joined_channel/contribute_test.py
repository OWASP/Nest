from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.common.gsoc import GSOC_2025_MILESTONES
from apps.slack.constants import (
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.member_joined_channel.contribute import Contribute
from apps.slack.utils import get_text


class TestContributeEventHandler:
    @pytest.fixture
    def mock_slack_event(self):
        return {"user": "U123456", "channel": OWASP_CONTRIBUTE_CHANNEL_ID.replace("#", "")}

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("events_enabled", "project_count", "issue_count", "expected_messages"),
        [
            (False, 0, 0, []),
            (
                True,
                20,
                50,
                [
                    "20 active OWASP projects",
                    "50 recently opened issues",
                    NEST_BOT_NAME,
                    "/contribute",
                    "You can share feedback on your NestBot experience",
                ],
            ),
        ],
    )
    @patch("apps.owasp.models.project.Project.active_projects_count")
    @patch("apps.github.models.issue.Issue.open_issues_count")
    @patch("apps.common.utils.get_absolute_url", return_value="/contribute")
    def test_handler_responses(
        self,
        mock_get_absolute_url,
        mock_open_issues_count,
        mock_active_projects_count,
        events_enabled,
        project_count,
        issue_count,
        expected_messages,
        mock_slack_event,
        mock_slack_client,
    ):
        settings.SLACK_EVENTS_ENABLED = events_enabled
        mock_active_projects_count.return_value = project_count
        mock_open_issues_count.return_value = issue_count

        contribute = Contribute()
        contribute.handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

        if not events_enabled:
            mock_slack_client.chat_postEphemeral.assert_not_called()
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            mock_slack_client.chat_postEphemeral.assert_called_once_with(
                blocks=GSOC_2025_MILESTONES,
                channel=mock_slack_event["channel"],
                user=mock_slack_event["user"],
                text=get_text(GSOC_2025_MILESTONES),
            )

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

            mock_active_projects_count.assert_called_once()
            mock_open_issues_count.assert_called_once()

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
