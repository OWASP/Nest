"""Slack bot staff command."""

from apps.common.constants import OWASP_URL
from apps.owasp.utils.staff import get_staff_data
from apps.slack.commands.command import CommandBase


class Staff(CommandBase):
    """Slack bot /staff command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        items = get_staff_data()
        return {
            **super().get_context(command),
            "ITEMS": items,
            "STAFF_PAGE_NAME": "OWASP Foundation Staff",
            "STAFF_PAGE_URL": f"{OWASP_URL}/corporate/",
        }
