"""Slack bot contact command."""

from apps.slack.commands.command import CommandBase


class Contact(CommandBase):
    """Slack bot /contact command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "navigate.template"

    def get_template_context(self, command):
        """Get the template context."""
        return {
            **super().get_template_context(command),
            "url": "https://owasp.org/contact/",
            "name": "OWASP contact",
        }
