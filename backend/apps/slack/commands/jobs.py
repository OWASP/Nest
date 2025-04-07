"""Slack bot jobs command."""

from apps.common.constants import NL
from apps.slack.commands.command import CommandBase
from apps.slack.constants import (
    NEST_BOT_NAME,
    OWASP_JOBS_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
)


class Jobs(CommandBase):
    """Slack bot /jobs command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        return self.get_template_file().render(
            jobs_channel=OWASP_JOBS_CHANNEL_ID,
            feedback_channel=OWASP_PROJECT_NEST_CHANNEL_ID,
            nest_bot_name=NEST_BOT_NAME,
            NL=NL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
        )
