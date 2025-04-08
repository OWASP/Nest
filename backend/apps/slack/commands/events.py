"""Slack bot events command."""

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_events_data


class Events(CommandBase):
    """Slack bot /events command."""

    def get_template_context(self, command):
        """Get the template context."""
        events_data = get_events_data()
        valid_events = [event for event in events_data if event.start_date]
        sorted_events = sorted(valid_events, key=lambda x: x.start_date)

        categorized_events = {}
        for event in sorted_events:
            category = event.category or "Other"
            if category not in categorized_events:
                categorized_events[category] = {"events": []}
            categorized_events[category]["events"].append(
                {
                    "name": event.name,
                    "url": event.url,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "description": event.description,
                }
            )

        return {
            **super().get_template_context(command),
            "categorized_events": categorized_events,
            "website_url": OWASP_WEBSITE_URL,
        }
