"""Slack bot jobs command."""

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_JOBS_CHANNEL_ID


class Jobs(CommandBase):
    """Slack bot /jobs command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        return self.get_template_file().render(
            jobs_channel=OWASP_JOBS_CHANNEL_ID, feedback_message=FEEDBACK_CHANNEL_MESSAGE, NL=NL
        )
