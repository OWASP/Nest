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
    matchers = [lambda event: event["channel"] == OWASP_GSOC_CHANNEL_ID.lstrip("#")]

    def get_context(self, event):
        """Get the template context.

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        return {
            "FEEDBACK_CHANNEL_MESSAGE": FEEDBACK_CHANNEL_MESSAGE,
            "gsoc_channel_id": OWASP_GSOC_CHANNEL_ID,
            "gsoc_info_blocks": GSOC_GENERAL_INFORMATION_BLOCKS,
            "user_id": event["user"],
        }

    def handle_event(self, event, client):
        """Handle the member_joined_channel event for the GSoC channel."""
        client.chat_postEphemeral(
            blocks=GSOC_2025_MILESTONES,
            channel=event["channel"],
            text=get_text(GSOC_2025_MILESTONES),
            user=event["user"],
        )
        super().handle_event(event, client)
