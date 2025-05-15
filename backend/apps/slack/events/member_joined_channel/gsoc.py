"""Slack member joined #gsoc channel handler using templates."""

import logging

from apps.slack.common.gsoc import GSOC_2025_MILESTONES, GSOC_GENERAL_INFORMATION_BLOCKS
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_GSOC_CHANNEL_ID
from apps.slack.events.event import EventBase
from apps.slack.utils import get_text

logger: logging.Logger = logging.getLogger(__name__)


class Gsoc(EventBase):
    """Slack GSoC channel join event handler."""

    event_type = "member_joined_channel"

    def __init__(self):
        """Initialize the GSoC event handler."""
        super().__init__()
        self.matchers = [lambda event: f"#{event['channel']}" == OWASP_GSOC_CHANNEL_ID]

    def get_context(self, event):
        """Get the template context.

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        return {
            "user_id": event["user"],
            "gsoc_channel_id": OWASP_GSOC_CHANNEL_ID,
            "gsoc_info_blocks": GSOC_GENERAL_INFORMATION_BLOCKS,
            "FEEDBACK_CHANNEL_MESSAGE": FEEDBACK_CHANNEL_MESSAGE,
        }

    def handle_event(self, event, client):
        """Handle the member_joined_channel event for the GSoC channel."""
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
