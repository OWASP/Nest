"""Slack bot committees command."""

from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase
from apps.slack.common.handlers.committees import get_blocks
from apps.slack.common.presentation import EntityPresentation


class Committees(CommandBase):
    """Slack bot /committees command."""

    def get_render_blocks(self, command):
        """Get the rendered blocks."""
        search_query = command["text"].strip()
        return get_blocks(
            search_query=search_query,
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