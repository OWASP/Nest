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

    # Add 👀 reaction to indicate bot is processing
    try:
        client.reactions_add(
            channel=message.conversation.slack_channel_id,
            timestamp=message.slack_message_id,
            name="eyes",
        )
    except SlackApiError as e:
        logger.warning(f"Failed to add reaction: {e}")

    ai_response_text = process_ai_query(query=message.text)
    if not ai_response_text:
        return

    client.chat_postMessage(
        channel=message.conversation.slack_channel_id,
        blocks=get_blocks(ai_response_text),
        text=ai_response_text,
        thread_ts=message.slack_message_id,
    )
