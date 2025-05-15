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

    def __init__(self):
        """Initialize the Contribute event handler."""
        super().__init__()
        self.matchers = [lambda event: f"#{event['channel']}" == OWASP_CONTRIBUTE_CHANNEL_ID]

    def get_context(self, event):
        """Get the context .

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        from apps.github.models.issue import Issue
        from apps.owasp.models.project import Project

        user_id = event["user"]
        return {
            "user_id": user_id,
            "contribute_channel_id": OWASP_CONTRIBUTE_CHANNEL_ID,
            "active_projects_count": Project.active_projects_count(),
            "open_issues_count": Issue.open_issues_count(),
            "nest_bot_name": NEST_BOT_NAME,
            "contribute_url": get_absolute_url("/contribute"),
            "FEEDBACK_CHANNEL_MESSAGE": FEEDBACK_CHANNEL_MESSAGE,
        }

    def handle_event(self, event, client):
        """Handle the member_joined_channel event for the contribute channel."""
        user_id = event["user"]
        client.chat_postEphemeral(
            blocks=GSOC_2025_MILESTONES,
            channel=event["channel"],
            user=user_id,
            text=get_text(GSOC_2025_MILESTONES),
        )
        conv = self.open_conversation(client, user_id)
        if conv:
            context = self.get_context(event)
            client.chat_postMessage(
                blocks=self.get_render_blocks(context),
                channel=conv["channel"]["id"],
                text=get_text(self.get_render_blocks(context)),
            )
