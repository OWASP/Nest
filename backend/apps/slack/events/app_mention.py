"""Slack app mention event handler."""

import contextlib
import logging

import django_rq
from slack_sdk.errors import SlackApiError

from apps.slack.events.event import EventBase
from apps.slack.models import Conversation

logger = logging.getLogger(__name__)

ALLOWED_MIMETYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB


class AppMention(EventBase):
    """Handles app mention events when the bot is mentioned in a channel."""

    event_type = "app_mention"

    def handle_event(self, event, client):
        """Handle an incoming app mention event."""
        channel_id = event.get("channel")
        files = event.get("files", [])
        text = event.get("text", "")

        if not Conversation.objects.filter(
            is_nest_bot_assistant_enabled=True,
            slack_channel_id=channel_id,
        ).exists():
            logger.warning("NestBot AI Assistant is not enabled for this conversation.")
            return

        images_raw = [
            file
            for file in files
            if file.get("mimetype") in ALLOWED_MIMETYPES
            and file.get("size", float("inf")) <= MAX_IMAGE_SIZE
        ]

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
        except Exception as e:
            logger.exception(
                "Exception while adding reaction to message",
                extra={
                    "channel_id": channel_id,
                    "message_ts": message_ts,
                    "error": str(e),
                },
            )

        slack_image_files = [
            {"url_private": image.get("url_private"), "mimetype": image.get("mimetype")}
            for image in images_raw
            if image.get("url_private")
        ]

        try:
            from apps.slack.services.message_auto_reply import process_ai_query_async

            django_rq.get_queue("ai").enqueue(
                process_ai_query_async,
                query=query,
                channel_id=channel_id,
                message_ts=message_ts,
                thread_ts=thread_ts,
                is_app_mention=True,
                slack_image_files=slack_image_files or None,
            )
        except Exception as e:
            with contextlib.suppress(SlackApiError):
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )

            with contextlib.suppress(SlackApiError):
                client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        "⚠️ An error occurred while processing your query. Please try again later."
                    ),
                    thread_ts=thread_ts or message_ts,
                )

            logger.exception(
                "Failed to enqueue AI query processing",
                extra={
                    "channel_id": channel_id,
                    "message_ts": message_ts,
                    "thread_ts": thread_ts,
                    "query": query[:100],
                    "error": str(e),
                },
            )
            raise
