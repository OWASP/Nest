"""Slack member joined #gsoc channel handler using templates."""

import logging
from pathlib import Path

from apps.common.utils import convert_to_snake_case
from apps.slack.constants import OWASP_PROJECT_NEST_CHANNEL_ID
from apps.slack.events.event import EventBase

logger: logging.Logger = logging.getLogger(__name__)


class ProjectNest(EventBase):
    """Slack project-nest channel join event handler."""

    event_type = "member_joined_channel"
    matchers = [lambda event: event["channel"] == OWASP_PROJECT_NEST_CHANNEL_ID.lstrip("#")]

    @property
    def direct_message_template_path(self) -> Path | None:
        """Get direct message template path.

        Returns:
            Path: The template file path.

        """
        return None

    @property
    def ephemeral_message_template_path(self) -> Path:
        """Get ephemeral message template path.

        Returns:
            Path: The template file path.

        """
        return Path(
            f"events/{self.event_type}/"
            f"{convert_to_snake_case(self.__class__.__name__)}/"
            "ephemeral_message.jinja"
        )

    def get_context(self, event):
        """Get the template context.

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(event),
            "PROJECT_NEST_CHANNEL_ID": OWASP_PROJECT_NEST_CHANNEL_ID,
            "PROJECT_NEST_CHANNEL_NAME": "project-nest",
        }
