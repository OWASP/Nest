"""Slack service tasks for background processing."""

import logging
import time

from django.db import DatabaseError
from django_rq import job
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.handlers.ai import get_blocks, process_ai_query
from apps.slack.models import Message
from apps.slack.models.bot_interaction import BotInteraction
from apps.slack.services.channel_router import route

logger = logging.getLogger(__name__)


@job("ai")
def generate_ai_reply_if_unanswered(message_id: int):
    """Check if a message is still unanswered and generate an AI reply or redirect."""
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

    start_time = time.monotonic()

    route_result = route(message.text)
    if route_result:
        channel_id, label = route_result
        redirect_text = f"This sounds like a question for <{channel_id}|#{label}>! 👋"
        response = client.chat_postMessage(
            channel=message.conversation.slack_channel_id,
            blocks=[markdown(redirect_text)],
            text=redirect_text,
            thread_ts=message.slack_message_id,
        )
        latency_ms = int((time.monotonic() - start_time) * 1000)
        reply_ts = response.get("ts", "") if response else ""
        logger.info(
            "NestBot redirected message",
            extra={
                "channel_id": message.conversation.slack_channel_id,
                "intent_category": label,
                "routed_to_channel": channel_id,
                "latency_ms": latency_ms,
                "redirect": True,
            },
        )
        _save_interaction(
            message=message,
            bot_response=redirect_text,
            reply_ts=reply_ts,
            intent_category=label,
        )
        return

    ai_response_text = process_ai_query(query=message.text)
    if not ai_response_text:
        return

    response = client.chat_postMessage(
        channel=message.conversation.slack_channel_id,
        blocks=get_blocks(ai_response_text),
        text=ai_response_text,
        thread_ts=message.slack_message_id,
    )

    latency_ms = int((time.monotonic() - start_time) * 1000)
    reply_ts = response.get("ts", "") if response else ""
    logger.info(
        "NestBot answered message",
        extra={
            "channel_id": message.conversation.slack_channel_id,
            "intent_category": "general_owasp",
            "latency_ms": latency_ms,
            "redirect": False,
        },
    )
    _save_interaction(
        message=message,
        bot_response=ai_response_text,
        reply_ts=reply_ts,
        intent_category="general_owasp",
    )


def _save_interaction(
    *, message: Message, bot_response: str, reply_ts: str, intent_category: str
) -> None:
    """Persist a BotInteraction record after posting a reply.

    Args:
        message: The original Slack message.
        bot_response: The text sent back to Slack.
        reply_ts: The Slack ts of the reply message.
        intent_category: Routing label or 'general_owasp'.

    """
    try:
        BotInteraction.objects.create(
            channel_id=message.conversation.slack_channel_id,
            user_id=message.raw_data.get("user", ""),
            user_message=message.text,
            bot_response=bot_response,
            intent_category=intent_category,
            slack_reply_ts=reply_ts,
        )
    except DatabaseError:
        logger.exception(
            "Failed to persist BotInteraction after sending Slack reply",
            extra={
                "channel_id": message.conversation.slack_channel_id,
                "reply_ts": reply_ts,
            },
        )
