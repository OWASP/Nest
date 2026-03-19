"""Slack service tasks for background processing."""

import logging

from django_rq import job
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.ai import format_blocks, process_ai_query
from apps.slack.models import Message
from apps.slack.utils import format_ai_response_for_slack

logger = logging.getLogger(__name__)

# Plain-text fallback for chat.postMessage (notifications, clients without block support)
_FALLBACK_TEXT_MAX = 3000


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
    ai_response_text = process_ai_query(query=message.text, channel_id=channel_id)
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

    blocks = format_blocks(ai_response_text)
    plain = format_ai_response_for_slack(ai_response_text)
    if len(plain) > _FALLBACK_TEXT_MAX:
        cut = _FALLBACK_TEXT_MAX - 1
        plain = f"{plain[:cut]}…"
    if not plain.strip():
        plain = "\u2014"

    client.chat_postMessage(
        channel=channel_id,
        blocks=blocks,
        text=plain,
        thread_ts=message.slack_message_id,
    )
