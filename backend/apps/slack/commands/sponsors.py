"""Slack bot sponsors command."""

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.constants import NEST_BOT_NAME, OWASP_PROJECT_NEST_CHANNEL_ID
from apps.slack.utils import get_sponsors_data


class Sponsors(CommandBase):
    """Slack bot /sponsors command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        sponsors = get_sponsors_data()
        if not sponsors:
            return self.get_template_file().render(has_sponsors=False, NL=NL)
        return self.get_template_file().render(
            has_sponsors=True,
            sponsors=sponsors,
            website_url=OWASP_WEBSITE_URL,
            feedback_channel=OWASP_PROJECT_NEST_CHANNEL_ID,
            nest_bot_name=NEST_BOT_NAME,
            NL=NL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
        )
