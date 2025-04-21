"""Slack bot staff command."""

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_staff_data


class Staff(CommandBase):
    """Slack bot /staff command."""

    def get_template_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        items = get_staff_data()
        return {
            **super().get_template_context(command),
            "items": items,
            "website_url": OWASP_WEBSITE_URL,
        }
