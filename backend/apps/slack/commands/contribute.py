"""Slack bot contribute command."""

from apps.common.constants import NL
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_HELP, COMMAND_START
from apps.slack.common.handlers.contribute import get_blocks
from apps.slack.common.presentation import EntityPresentation


class Contribute(CommandBase):
    """Slack bot /contribute command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        template = self.get_template_file()
        return template.render(NL=NL)

    def get_render_blocks(self, command):
        """Get the rendered blocks."""
        command_text = command["text"].strip()
        if command_text in COMMAND_HELP:
            return super().get_render_blocks(command)
        search_query = "" if command_text in COMMAND_START else command_text
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
