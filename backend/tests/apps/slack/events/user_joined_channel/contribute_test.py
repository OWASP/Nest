from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.member_joined_channel.contribute import contribute_handler


class TestContributeEventHandler:
    @pytest.fixture
    def mock_slack_event(self):
        return {"user": "U123456", "channel": OWASP_CONTRIBUTE_CHANNEL_ID}

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
                    "/contribute --start",
                    FEEDBACK_CHANNEL_MESSAGE.strip(),
                ],
            ),
        ],
    )
    @patch("apps.owasp.models.project.Project.active_projects_count")
    @patch("apps.github.models.issue.Issue.open_issues_count")
    def test_handler_responses(
        self,
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

        contribute_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

        if not events_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            mock_slack_client.conversations_open.assert_called_once_with(users="U123456")
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

            for message in expected_messages:
                assert any(message in str(block) for block in blocks)

            mock_active_projects_count.assert_called_once()
            mock_open_issues_count.assert_called_once()

    @pytest.mark.parametrize(
        ("channel_id", "expected_result"),
        [
            (OWASP_CONTRIBUTE_CHANNEL_ID, True),
            ("C999999", False),
        ],
    )
    def test_check_contribute_handler(self, channel_id, expected_result):
        contribute_module = __import__(
            "apps.slack.events.member_joined_channel.contribute",
            fromlist=["contribute_handler"],
        )
        check_contribute_handler = getattr(
            contribute_module,
            "check_contribute_handler",
            lambda x: x.get("channel") == OWASP_CONTRIBUTE_CHANNEL_ID,
        )

        assert check_contribute_handler({"channel": channel_id}) == expected_result
