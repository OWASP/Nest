"""Slack app mention event handler."""

import logging

from apps.slack.blocks import markdown
from apps.slack.common.handlers.ai import get_blocks
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation

logger = logging.getLogger(__name__)


class AppMention(EventBase):
    """Handles app mention events when the bot is mentioned in a channel."""

    event_type = "app_mention"

    def handle_event(self, event, client):
        """Handle an incoming app mention event."""
        channel_id = event.get("channel")
        text = event.get("text", "")

        if not Conversation.objects.filter(
            is_nest_bot_assistant_enabled=True,
            slack_channel_id=channel_id,
        ).exists():
            logger.warning("NestBot AI Assistant is not enabled for this conversation.")
            return

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

        thread_ts = event.get("thread_ts") or event.get("ts")

        placeholder = client.chat_postMessage(
            channel=channel_id,
            blocks=[markdown("⏳ Thinking…")],
            text="Thinking…",
            thread_ts=thread_ts,
        )

        reply_blocks = get_blocks(query=query)
        client.chat_update(
            channel=channel_id,
            ts=placeholder["ts"],
            blocks=reply_blocks,
            text=query,
        )
