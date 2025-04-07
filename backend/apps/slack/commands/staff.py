"""Slack bot staff command."""

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_staff_data


class Staff(CommandBase):
    """Slack bot /staff command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        items = get_staff_data()
        if not items:
            return self.get_template_file().render(has_staff=False, NL=NL)
        return self.get_template_file().render(
            has_staff=True,
            items=items,
            NL=NL,
            website_url=OWASP_WEBSITE_URL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
        )
