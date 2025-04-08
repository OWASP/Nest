"""Slack bot staff command."""

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_staff_data


class Staff(CommandBase):
    """Slack bot /staff command."""

    def get_template_context(self, command):
        """Get the template context."""
        context = super().get_template_context(command)
        items = get_staff_data()
        context.update(
            {
                "has_staff": bool(items),
                "items": items,
                "website_url": OWASP_WEBSITE_URL,
            }
        )
        return context
