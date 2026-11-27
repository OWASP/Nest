"""Slack bot contribute command."""

from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_HELP, COMMAND_START
from apps.slack.common.handlers.contribute import get_blocks
from apps.slack.common.presentation import EntityPresentation


class Contribute(CommandBase):
    """Slack bot /contribute command."""

    def render_blocks(self, command):
        """Get the rendered blocks.

        Args:
            command (dict): The Slack command payload.

        Returns:
            list: A list of Slack blocks representing the projects.

        """
        command_text = command["text"].strip()
        if command_text in COMMAND_HELP:
            return super().render_blocks(command)

        return get_blocks(
            search_query="" if command_text in COMMAND_START else command_text,
            limit=10,
            presentation=EntityPresentation(
                include_feedback=True,
                include_metadata=True,
                include_pagination=False,
                include_timestamps=True,
                name_truncation=80,
                summary_truncation=300,
            ),
        )
