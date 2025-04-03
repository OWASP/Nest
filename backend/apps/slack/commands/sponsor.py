"""Slack bot sponsors command."""

from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase


class Sponsor(CommandBase):
    """Slack bot /sponsor command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        return "Coming soon..."


if SlackConfig.app:
    Sponsor().config_command()
