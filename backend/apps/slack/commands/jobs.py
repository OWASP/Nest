"""Slack bot jobs command."""

from apps.slack.commands.command import CommandBase
from apps.slack.constants import (
    NEST_BOT_NAME,
    OWASP_JOBS_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
)


class Jobs(CommandBase):
    """Slack bot /jobs command."""

    def get_template_context(self, command):
        """Get the template context."""
        context = super().get_template_context(command)
        context.update(
            {
                "jobs_channel": OWASP_JOBS_CHANNEL_ID,
                "feedback_channel": OWASP_PROJECT_NEST_CHANNEL_ID,
                "nest_bot_name": NEST_BOT_NAME,
            }
        )
        return context
