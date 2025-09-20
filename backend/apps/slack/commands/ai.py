"""Slack bot AI command."""

from apps.slack.commands.command import CommandBase


class Ai(CommandBase):
    """Slack bot /ai command."""

    def render_blocks(self, command: dict):
        """Get the rendered blocks.

        Args:
            command (dict): The Slack command payload.

        Returns:
            list: A list of Slack blocks representing the AI response.

        """
        from apps.slack.common.handlers.ai import get_blocks

        return get_blocks(
            query=command["text"].strip(),
        )
