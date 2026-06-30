"""Slack bot donate command."""

from apps.common.constants import OWASP_URL
from apps.slack.commands.command import CommandBase


class Donate(CommandBase):
    """Slack bot /donate command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "DONATION_PAGE_NAME": "OWASP Foundation",
            "DONATION_PAGE_URL": f"{OWASP_URL}/donate/",
            "DONATION_POLICY_PAGE_NAME": "OWASP Donations Policy",
            "DONATION_POLICY_PAGE_URL": f"{OWASP_URL}/www-policy/operational/donations",
        }
