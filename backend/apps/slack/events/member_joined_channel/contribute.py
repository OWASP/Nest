"""Slack member joined #contribute channel handler using templates."""

from apps.common.utils import get_absolute_url
from apps.slack.common.gsoc import GSOC_2025_MILESTONES
from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.event import EventBase
from apps.slack.utils import get_text


class Contribute(EventBase):
    """Slack contribute channel join event handler."""

    event_type = "member_joined_channel"
    matchers = [lambda event: event["channel"] == OWASP_CONTRIBUTE_CHANNEL_ID.lstrip("#")]

    def get_context(self, event):
        """Get the context .

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        from apps.github.models.issue import Issue
        from apps.owasp.models.project import Project

        return {
            "active_projects_count": Project.active_projects_count(),
            "contribute_channel_id": OWASP_CONTRIBUTE_CHANNEL_ID,
            "contribute_url": get_absolute_url("/contribute"),
            "FEEDBACK_CHANNEL_MESSAGE": FEEDBACK_CHANNEL_MESSAGE,
            "nest_bot_name": NEST_BOT_NAME,
            "open_issues_count": Issue.open_issues_count(),
            "user_id": event["user"],
        }

    def handle_event(self, event, client):
        """Handle the member_joined_channel event for the contribute channel."""
        client.chat_postEphemeral(
            blocks=GSOC_2025_MILESTONES,
            channel=event["channel"],
            text=get_text(GSOC_2025_MILESTONES),
            user=event["user"],
        )
        super().handle_event(event, client)
