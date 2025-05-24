"""Slack member joined #gsoc channel handler using templates."""

import logging

from apps.common.utils import convert_to_snake_case
from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS, OWASP_NEST_MILESTONES
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_GSOC_CHANNEL_ID
from apps.slack.events.event import EventBase

logger: logging.Logger = logging.getLogger(__name__)


class Gsoc(EventBase):
    """Slack GSoC channel join event handler."""

    event_type = "member_joined_channel"
    matchers = [lambda event: event["channel"] == OWASP_GSOC_CHANNEL_ID.lstrip("#")]

    @property
    def ephemeral_message(self) -> tuple | None:
        """Return ephemeral message text."""
        # TODO(arkid15r): Implement ephemeral message logic using templates.
        return OWASP_NEST_MILESTONES

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
            "user_id": self.get_user_id(event),
        }

    def get_template_file_name(self):
        """Get the template file name for this event handler.

        Returns:
            str: The template file name in snake_case.

        """
        return f"events/{self.event_type}/{convert_to_snake_case(self.__class__.__name__)}.jinja"
