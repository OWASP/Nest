"""Slack app mention event handler."""

import base64
import logging

from apps.slack.common.handlers.ai import get_blocks
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation
from apps.slack.utils import download_file

logger = logging.getLogger(__name__)

ALLOWED_MIMETYPES = ("image/jpeg", "image/png", "image/webp")
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
            if file.get("mimetype") in ALLOWED_MIMETYPES and file.get("size") <= MAX_IMAGE_SIZE
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
            result = client.reactions_add(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
            if result.get("ok"):
                logger.info("Successfully added 👀 reaction to message")
            else:
                error = result.get("error")
                # Handle common errors gracefully
                if error == "already_reacted":
                    logger.debug("Reaction already exists on message")
                else:
                    logger.warning(
                        "Failed to add reaction: %s",
                        error,
                        extra={
                            "channel_id": channel_id,
                            "message_ts": message_ts,
                            "response": result,
                        },
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

        image_uris = []
        for image in images_raw:
            content = download_file(image.get("url_private"), client.token)
            if content:
                image_uri = (
                    f"data:{image.get('mimetype')};base64,{base64.b64encode(content).decode()}"
                )
                image_uris.append(image_uri)

        # Get AI response and post it
        reply_blocks = get_blocks(
            query=query, images=image_uris, channel_id=channel_id, is_app_mention=True
        )
        client.chat_postMessage(
            channel=channel_id,
            blocks=reply_blocks,
            text=query,
            thread_ts=thread_ts,
        )
