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

        logger.info(
            "Handling app mention",
            extra={"channel_id": channel_id, "query": query[:100]},
        )

        thread_ts = event.get("thread_ts") or event.get("ts")
        message_ts = event.get("ts")

        try:
            client.reactions_add(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
        except Exception:
            logger.exception("Failed to add reaction to message")

        # Process query in the background
        import django_rq

        from apps.slack.services.message_auto_reply import (
            process_ai_query_async,
        )

        django_rq.get_queue("ai").enqueue(
            process_ai_query_async,
            query=query,
            channel_id=channel_id,
            message_ts=message_ts,
            thread_ts=thread_ts,
            is_app_mention=True,
        )
