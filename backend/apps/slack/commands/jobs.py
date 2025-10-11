"""Slack bot jobs command."""

from apps.slack.commands.command import CommandBase
from apps.slack.constants import OWASP_JOBS_CHANNEL_ID


class Jobs(CommandBase):
    """Slack bot /jobs command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "JOBS_CHANNEL_ID": OWASP_JOBS_CHANNEL_ID,
        }
