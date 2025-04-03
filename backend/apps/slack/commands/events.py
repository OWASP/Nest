"""Slack bot events command."""

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_events_data


class Events(CommandBase):
    """Slack bot /events command."""

    def get_render_text(self, command):
        """Get the rendered text."""
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

        return self.get_template_file().render(
            categorized_events=categorized_events,
            website_url=OWASP_WEBSITE_URL,
            NL=NL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
        )


if SlackConfig.app:
    Events().config_command()
