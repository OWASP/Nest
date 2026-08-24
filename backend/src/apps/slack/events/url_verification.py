"""Slack URL verification event handler."""

from apps.slack.events.event import EventBase


class UrlVerification(EventBase):
    """Handle Slack URL verification events."""

    event_type = "url_verification"

    def handler(self, event, client, ack):
        """Acknowledge Slack URL verification challenges."""
        ack(event["challenge"])
