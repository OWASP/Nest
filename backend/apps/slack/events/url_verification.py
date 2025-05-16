"""Slack URL verification event handler."""

from apps.slack.events.event import EventBase


class UrlVerification(EventBase):
    """Handle Slack URL verification events."""

    event_type = "url_verification"

    def handle_event(self, event, client):
        """Handle the URL verification event."""
        return event["challenge"]
