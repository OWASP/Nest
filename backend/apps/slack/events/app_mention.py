"""Slack app mention event handler."""

import logging

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

        # Add 👀 reaction to indicate bot is processing
        try:
            client.reactions_add(
                channel=channel_id,
                timestamp=thread_ts,
                name="eyes",
            )
        except Exception as e:
            logger.warning(f"Failed to add reaction: {e}")

        # Generate and post AI response
        try:
            reply_blocks = get_blocks(query=query)
            client.chat_postMessage(
                channel=channel_id,
                blocks=reply_blocks,
                text=query,
                thread_ts=thread_ts,
            )
        except Exception as e:
            logger.error(f"Failed to generate or post AI response: {e}")
            # Reaction stays visible even if AI response fails
