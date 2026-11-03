"""Slack bot projects command."""

from apps.slack.commands.command import CommandBase
from apps.slack.common.handlers.projects import get_blocks
from apps.slack.common.presentation import EntityPresentation


class Projects(CommandBase):
    """Slack bot /projects command."""

    def render_blocks(self, command: dict):
        """Get the rendered blocks.

        Args:
            command (dict): The Slack command payload.

        Returns:
            list: A list of Slack blocks representing the projects.

        """
        return get_blocks(
            search_query=command["text"].strip(),
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
