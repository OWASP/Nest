"""Slack bot donate command."""

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase


class Donate(CommandBase):
    """Slack bot /donate command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        return self.get_template_file().render(
            website_url=OWASP_WEBSITE_URL,
            NL=NL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
        )