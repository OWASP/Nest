"""Slack service tasks for background processing."""

import logging

from django_rq import job
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.ai import get_blocks, process_ai_query
from apps.slack.models import Message

logger = logging.getLogger(__name__)


@job("ai")
def generate_ai_reply_if_unanswered(message_id: int):
    """Check if a message is still unanswered and generate AI reply."""
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return

    if not message.conversation.is_nest_bot_assistant_enabled:
        return

    if not SlackConfig.app:
        logger.warning("Slack app is not configured")
        return

    client = SlackConfig.app.client

    try:
        result = client.conversations_replies(
            channel=message.conversation.slack_channel_id,
            ts=message.slack_message_id,
            limit=1,
        )
        if result.get("messages") and result["messages"][0].get("reply_count", 0) > 0:
            return

    except SlackApiError:
        logger.exception("Error checking for replies for message")

    channel_id = message.conversation.slack_channel_id
    query_text = message.text_with_images if message.text_with_images else message.text
    ai_response_text = process_ai_query(query=query_text, channel_id=channel_id)
    if not ai_response_text:
        # Add shrugging reaction when no answer can be generated
        try:
            result = client.reactions_add(
                channel=channel_id,
                timestamp=message.slack_message_id,
                name="man-shrugging",
            )
            if result.get("ok"):
                logger.info("Successfully added 🤷 reaction to message")
            else:
                error = result.get("error")
                if error != "already_reacted":
                    logger.warning(
                        "Failed to add reaction: %s",
                        error,
                        extra={
                            "channel_id": channel_id,
                            "message_id": message.slack_message_id,
                        },
                    )
        except SlackApiError:
            logger.exception("Error adding reaction to message")
        return

    client.chat_postMessage(
        channel=channel_id,
        blocks=get_blocks(ai_response_text, channel_id=channel_id),
        text=ai_response_text,
        thread_ts=message.slack_message_id,
    )
