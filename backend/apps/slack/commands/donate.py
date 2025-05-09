"""Slack bot donate command."""

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase


class Donate(CommandBase):
    """Slack bot /donate command."""

    def get_template_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_template_context(command),
            "website_url": OWASP_WEBSITE_URL,
        }
