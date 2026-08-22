"""Slack bot sponsors command."""

from apps.common.constants import OWASP_URL
from apps.owasp.models.sponsor import Sponsor
from apps.slack.commands.command import CommandBase


class Sponsors(CommandBase):
    """Slack bot /sponsors command."""

    def get_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "SPONSORS": Sponsor.objects.all()[:10],
            "SPONSORS_PAGE_NAME": "OWASP Supporters",
            "SPONSORS_PAGE_URL": f"{OWASP_URL}/supporters/",
        }
