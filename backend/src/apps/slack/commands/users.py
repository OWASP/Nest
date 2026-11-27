"""Slack bot users command."""

from apps.slack.commands.command import CommandBase
from apps.slack.common.handlers.users import get_blocks
from apps.slack.common.presentation import EntityPresentation


class Users(CommandBase):
    """Slack bot /users command."""

    def render_blocks(self, command: dict):
        """Get the rendered blocks."""
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
