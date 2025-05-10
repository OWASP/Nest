"""Slack bot app_home_opened event handler using templates."""

from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header
from apps.slack.events.event import EventBase


class AppHomeOpened(EventBase):
    """Slack bot home page."""

    event_type = "app_home_opened"

    def handle_event(self, event, client):
        """Handle the app_home_opened event."""
        user_id = event["user"]
        context = {
            "user_id": user_id,
            "TAB": "    ",  # 4 spaces for indentation
        }

        home_view = {"type": "home", "blocks": [*get_header(), *self.get_render_blocks(context)]}

        client.views_publish(user_id=user_id, view=home_view)


if SlackConfig.app:
    AppHomeOpened().register()
