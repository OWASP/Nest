"""Slack bot sponsors command."""

from apps.slack.commands.command import CommandBase


class Sponsor(CommandBase):
    """Slack bot /sponsor command."""

    def render_text(self, command):
        """Get the rendered text.

        Args:
            command (dict): The Slack command payload.

        Returns:
            string: The rendered text.

        """
        return "Coming soon..."
