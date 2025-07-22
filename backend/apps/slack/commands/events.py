"""Slack bot events command."""

from apps.common.constants import OWASP_URL
from apps.slack.commands.command import CommandBase


def get_events_data():
    """Get events data for the template."""
    # Local import to avoid AppRegistryNotReady exception.
    from apps.owasp.models.event import Event

    return [
        {
            "description": event.description,
            "end_date": event.end_date,
            "location": event.suggested_location,
            "name": event.name,
            "start_date": event.start_date,
            "url": event.url,
        }
        for event in sorted(Event.upcoming_events(), key=lambda e: e.start_date)
    ]


class Events(CommandBase):
    """Slack bot /events command."""

    def get_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "EVENTS": get_events_data(),
            "EVENTS_PAGE_NAME": "OWASP Events",
            "EVENTS_PAGE_URL": f"{OWASP_URL}/events/",
        }
