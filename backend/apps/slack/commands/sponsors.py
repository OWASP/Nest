"""Slack bot sponsors command."""

from apps.common.constants import OWASP_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_sponsors_data


class Sponsors(CommandBase):
    """Slack bot /sponsors command."""

    def get_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        sponsors = get_sponsors_data()
        return {
            **super().get_context(command),
            "SPONSORS": sponsors,
            "SPONSORS_PAGE_NAME": "OWASP Supporters",
            "SPONSORS_PAGE_URL": f"{OWASP_URL}/supporters/",
        }
