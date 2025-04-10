"""Slack bot community command."""

from apps.slack.commands.command import CommandBase


class Community(CommandBase):
    """Slack bot /community command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "navigate.template"

    def get_template_context(self, command):
        """Get the template context."""
        return {
            **super().get_template_context(command),
            "url": "https://nest.owasp.dev/community/users/",
            "name": "OWASP community",
        }
