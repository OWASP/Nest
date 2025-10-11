"""Slack member joined #contribute channel handler using templates."""

from pathlib import Path

from apps.common.utils import convert_to_snake_case, get_absolute_url
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_SPONSORSHIP_CHANNEL_ID,
)
from apps.slack.events.event import EventBase


class Contribute(EventBase):
    """Slack contribute channel join event handler."""

    event_type = "member_joined_channel"
    matchers = [lambda event: event["channel"] == OWASP_CONTRIBUTE_CHANNEL_ID.lstrip("#")]

    @property
    def direct_message_template_path(self) -> Path:
        """Get direct message template path.

        Returns:
            Path: The template file path.

        """
        return Path(
            f"events/{self.event_type}/"
            f"{convert_to_snake_case(self.__class__.__name__)}/"
            "direct_message.jinja"
        )

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

    def get_context(self, event: dict) -> dict:
        """Get the context.

        Args:
            event: The Slack event

        Returns:
            dict: The template context.

        """
        from apps.github.models.issue import Issue
        from apps.owasp.models.project import Project

        return {
            **super().get_context(event),
            "ACTIVE_PROJECTS_COUNT": Project.active_projects_count(),
            "CONTRIBUTE_CHANNEL_ID": OWASP_CONTRIBUTE_CHANNEL_ID,
            "CONTRIBUTE_PAGE_URL": get_absolute_url("/contribute"),
            "OPEN_ISSUES_COUNT": Issue.open_issues_count(),
            "PROJECT_NEST_CHANNEL_ID": OWASP_PROJECT_NEST_CHANNEL_ID,
            "SPONSORSHIP_CHANNEL_ID": OWASP_SPONSORSHIP_CHANNEL_ID,
        }
