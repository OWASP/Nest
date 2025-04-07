"""Slack bot contact command."""

from apps.common.constants import NL
from apps.slack.commands.command import CommandBase


class Contact(CommandBase):
    """Slack bot /contact command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "navigate.template"

    def get_render_text(self, command):
        """Get the rendered text."""
        return self.get_template_file().render(
            url="https://owasp.org/contact/", name="OWASP contact", NL=NL
        )
