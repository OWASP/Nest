"""Slack app mention event handler."""

import logging

from apps.slack.common.handlers.ai import get_blocks
from apps.slack.events.event import EventBase

logger = logging.getLogger(__name__)


class AppMention(EventBase):
    """Handles app mention events when the bot is mentioned in a channel."""

    event_type = "app_mention"

    def handle_event(self, event, client):
        """Handle an incoming app mention event."""
        channel_id = event.get("channel")
        text = event.get("text", "")

        query = text
        for mention in event.get("blocks", []):
            if mention.get("type") == "rich_text":
                for element in mention.get("elements", []):
                    if element.get("type") == "rich_text_section":
                        for text_element in element.get("elements", []):
                            if text_element.get("type") == "text":
                                query = text_element.get("text", "").strip()
                                break

        if not query:
            logger.warning("No query found in app mention")
            return

        logger.info("Handling app mention")

        reply_blocks = get_blocks(query=query)
        client.chat_postMessage(
            channel=channel_id,
            blocks=reply_blocks,
            text=query,
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )
