"""Slack bot community command."""

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase


class Community(CommandBase):
    """Slack bot /community command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "COMMUNITY_PAGE_NAME": "OWASP community",
            "COMMUNITY_PAGE_URL": get_absolute_url("/members"),
        }
