"""Slack member joined #owasp-community channel handler using templates."""

from pathlib import Path
from time import sleep

from apps.common.utils import convert_to_snake_case
from apps.slack.constants import OWASP_COMMUNITY_CHANNEL_ID
from apps.slack.events.event import EventBase


class OwaspCommunity(EventBase):
    """Slack owasp-community channel join event handler."""

    event_type = "member_joined_channel"
    matchers = [lambda event: event["channel"] == OWASP_COMMUNITY_CHANNEL_ID.lstrip("#")]

    @property
    def direct_message_template_path(self) -> Path | None:
        """Get direct message template path.

        Returns:
            Path | None: None — only an ephemeral welcome is sent.

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

    def handle_event(self, event, client):
        """Handle member_joined_channel for #owasp-community with a short delay.

        The delay gives Slack time to fully register a freshly joined user in the
        channel to reduce `user_not_in_channel` errors when posting ephemerals.
        """
        sleep(7)
        super().handle_event(event, client)
