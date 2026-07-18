"""Slack reaction_added event handler for bot reply feedback."""

import logging

from apps.slack.events.event import EventBase
from apps.slack.models.bot_interaction import BotInteraction

logger = logging.getLogger(__name__)

THUMBS_UP = "thumbsup"
THUMBS_DOWN = "thumbsdown"
FEEDBACK_REACTIONS = {THUMBS_UP, THUMBS_DOWN}


class BotFeedback(EventBase):
    """Records 👍 / 👎 reactions on NestBot replies."""

    event_type = "reaction_added"

    def handle_event(self, event, client):  # noqa: ARG002
        """Handle a reaction_added event.

        Checks whether the reacted-to message ts matches a BotInteraction
        slack_reply_ts. If so, records the feedback. Reactions on non-bot
        messages are silently ignored.

        Args:
            event (dict): The Slack reaction_added event payload.
            client: The Slack WebClient instance (unused but required by base).

        """
        reaction = event.get("reaction", "")
        if reaction not in FEEDBACK_REACTIONS:
            return

        item = event.get("item", {})
        if item.get("type") != "message":
            return

        reply_ts = item.get("ts", "")
        if not reply_ts:
            return

        channel_id = item.get("channel", "")
        if not channel_id:
            return

        interaction = (
            BotInteraction.objects.filter(
                slack_reply_ts=reply_ts, channel_id=channel_id
            )
            .order_by("-nest_created_at")
            .first()
        )
        if interaction is None:
            return

        interaction.thumbs_up = reaction == THUMBS_UP
        interaction.save(update_fields=["thumbs_up", "nest_updated_at"])

        logger.info(
            "Feedback recorded for BotInteraction pk=%s: %s",
            interaction.pk,
            "👍" if interaction.thumbs_up else "👎",
        )
