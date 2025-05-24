"""Slack member joined #contribute channel handler using templates."""

from apps.common.utils import convert_to_snake_case, get_absolute_url
from apps.slack.common.gsoc import OWASP_NEST_MILESTONES
from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.event import EventBase


class Contribute(EventBase):
    """Slack contribute channel join event handler."""

    event_type = "member_joined_channel"
    matchers = [lambda event: event["channel"] == OWASP_CONTRIBUTE_CHANNEL_ID.lstrip("#")]

    @property
    def ephemeral_message(self) -> tuple | None:
        """Return ephemeral message text."""
        # TODO(arkid15r): Implement ephemeral message logic using templates.
        return OWASP_NEST_MILESTONES

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
            "user_id": self.get_user_id(event),
        }

    def get_template_file_name(self):
        """Get the template file name for this event handler.

        Returns:
            str: The template file name in snake_case.

        """
        return f"events/{self.event_type}/{convert_to_snake_case(self.__class__.__name__)}.jinja"
