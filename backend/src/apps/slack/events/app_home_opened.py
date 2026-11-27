"""Slack bot app_home_opened event handler."""

from apps.slack.blocks import get_header
from apps.slack.events.event import EventBase


class AppHomeOpened(EventBase):
    """Slack bot home page."""

    event_type = "app_home_opened"

    def handle_event(self, event, client):
        """Handle the app_home_opened event."""
        client.views_publish(
            user_id=self.get_user_id(event),
            view={
                "blocks": [
                    *get_header(),
                    *self.render_blocks(
                        self.direct_message_template,
                        self.get_context(event),
                    ),
                ],
                "type": "home",
            },
        )
