"""Slack service tasks for background processing."""

import logging
from html import escape

from django.conf import settings
from django_rq import job
from slack_sdk.errors import SlackApiError, SlackClientError
from slack_sdk.web import WebClient

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.ai import get_response_blocks, process_ai_query
from apps.slack.models import Message

logger = logging.getLogger(__name__)


def _is_unanswered(client: WebClient, message: Message) -> bool:
    """Only allow a reply after Slack confirms the thread is unanswered."""
    try:
        result = client.conversations_history(
            channel=message.conversation.slack_channel_id,
            oldest=message.slack_message_id,
            latest=message.slack_message_id,
            inclusive=True,
            limit=1,
        )
    except SlackClientError:
        logger.exception("Error checking for replies for message")
        return False

    messages = result.get("messages")
    return (
        bool(messages)
        and messages[0].get("ts") == message.slack_message_id
        and messages[0].get("reply_count", 0) == 0
    )


@job("ai")
def generate_ai_reply_if_unanswered(message_id: int):
    """Check if a message is still unanswered and generate AI reply."""
    # Jobs may have been queued by an earlier, enabled release.
    if not settings.NESTBOT_AI_ASSISTANT_ENABLED or not SlackConfig.app:
        if settings.NESTBOT_AI_ASSISTANT_ENABLED:
            logger.warning("Slack app is not configured")
        return

    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return

    if not message.conversation.is_nest_bot_assistant_enabled:
        return

    client = SlackConfig.app.client

    if not _is_unanswered(client, message):
        return

    channel_id = message.conversation.slack_channel_id
    ai_response_text = process_ai_query(query=message.text, channel_id=channel_id)
    response_blocks = get_response_blocks(ai_response_text) if ai_response_text else None
    # Someone may have answered while the provider was generating a response.
    if not settings.NESTBOT_AI_ASSISTANT_ENABLED or not _is_unanswered(client, message):
        return
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
        blocks=response_blocks,
        text=escape(ai_response_text, quote=False),
        mrkdwn=False,
        parse="none",
        thread_ts=message.slack_message_id,
    )
