"""Handle Slack reaction_added events."""

from apps.slack.events.event import EventBase
from apps.slack.services.moderation import process_reaction_added


class ReactionAdded(EventBase):
    """Route reaction_added to moderation service for processing."""

    event_type = "reaction_added"

    def handle_event(self, event, client):
        """Handle report reactions added to Slack messages."""
        process_reaction_added(event, client)
