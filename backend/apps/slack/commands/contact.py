"""Slack bot contact command."""

from apps.slack.commands.command import CommandBase


class Contact(CommandBase):
    """Slack bot /contact command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "commands/navigate.jinja"

    def get_template_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_template_context(command),
            "name": "OWASP contact",
            "url": "https://owasp.org/contact/",
        }
