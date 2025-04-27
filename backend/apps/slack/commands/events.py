"""Slack bot events command."""

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_events_data


class Events(CommandBase):
    """Slack bot /events command."""

    def get_template_context(self, command):
        """Get the template context."""
        upcoming_events = [
            {
                "description": event.description,
                "end_date": event.end_date,
                "location": event.suggested_location,
                "name": event.name,
                "start_date": event.start_date,
                "url": event.url,
            }
            for event in sorted(get_events_data(), key=lambda e: e.start_date)
        ]

        return {
            **super().get_template_context(command),
            "upcoming_events": upcoming_events,
            "website_url": OWASP_WEBSITE_URL,
        }
