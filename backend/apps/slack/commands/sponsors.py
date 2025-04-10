"""Slack bot sponsors command."""

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.constants import NEST_BOT_NAME, OWASP_PROJECT_NEST_CHANNEL_ID
from apps.slack.utils import get_sponsors_data


class Sponsors(CommandBase):
    """Slack bot /sponsors command."""

    def get_template_context(self, command):
        """Get the template context."""
        sponsors = get_sponsors_data()
        return {
            **super().get_template_context(command),
            "has_sponsors": bool(sponsors),
            "sponsors": sponsors,
            "website_url": OWASP_WEBSITE_URL,
            "feedback_channel": OWASP_PROJECT_NEST_CHANNEL_ID,
            "nest_bot_name": NEST_BOT_NAME,
        }
