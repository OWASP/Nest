"""Slack bot board command."""

from apps.slack.commands.command import CommandBase


class Board(CommandBase):
    """Slack bot /board command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "BOARD_PAGE_NAME": "Global board",
            "BOARD_PAGE_URL": "https://owasp.org/www-board/",
        }
