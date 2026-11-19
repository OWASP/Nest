"""Slack bot AI command."""

from django.conf import settings

from apps.slack.blocks import markdown
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
        if not settings.NESTBOT_AI_ASSISTANT_ENABLED:
            return [markdown("NestBot AI assistant is currently disabled.")]

        from apps.slack.common.handlers.ai import get_blocks

        return get_blocks(
            query=command["text"].strip(),
        )
