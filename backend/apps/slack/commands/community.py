"""Slack bot community command."""

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase


class Community(CommandBase):
    """Slack bot /community command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "navigate.template"

    def get_render_text(self, command):
        """Get the rendered text."""
        return self.get_template_file().render(
            url="https://nest.owasp.dev/community/users/",
            name="OWASP community",
            NL=NL,
        )
