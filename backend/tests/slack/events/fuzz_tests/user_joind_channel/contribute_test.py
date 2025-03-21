from unittest.mock import MagicMock, patch

from django.conf import settings

from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.member_joined_channel.contribute import contribute_handler

from hypothesis import given, strategies as st

class TestContributeEventHandler:
    @given(
        events_enabled=st.booleans(),
        project_count=st.integers(),
        issue_count=st.integers(),
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
    ):
        settings.SLACK_EVENTS_ENABLED = events_enabled
        mock_active_projects_count.return_value = project_count
        mock_open_issues_count.return_value = issue_count
        mock_slack_event = {"user": "U123456", "channel": OWASP_CONTRIBUTE_CHANNEL_ID}
        mock_slack_client = MagicMock()
        mock_slack_client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        

        contribute_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())
        
        assert True
