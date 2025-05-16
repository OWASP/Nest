"""Slack bot board command."""

from apps.slack.commands.command import CommandBase


class Board(CommandBase):
    """Slack bot /board command."""

    def get_template_file_name(self):
        """Get the template file name."""
        return "commands/navigate.jinja"

    def get_template_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            string: The rendered text.

        """
        return {
            **super().get_template_context(command),
            "name": "Global board",
            "url": "https://owasp.org/www-board/",
        }
