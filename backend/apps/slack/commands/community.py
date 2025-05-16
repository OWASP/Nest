"""Slack bot community command."""

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase


class Community(CommandBase):
    """Slack bot /community command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "commands/navigate.jinja"

    def get_template_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_template_context(command),
            "name": "OWASP community",
            "url": get_absolute_url("members"),
        }
