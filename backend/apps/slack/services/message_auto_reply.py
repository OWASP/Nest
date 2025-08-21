"""Slack service tasks for background processing."""

import logging

from django_rq import job
from slack_sdk import WebClient

from apps.slack.common.handlers.ai import get_blocks, process_ai_query
from apps.slack.models import Message

logger = logging.getLogger(__name__)


@job("default")
def generate_ai_reply_if_unanswered(message_id: int):
    """Check if a message is still unanswered and generate AI reply."""
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return

    if not message.conversation.is_nest_bot_assistant_enabled:
        return

    if message.thread_replies.exists():
        return

    ai_response_text = process_ai_query(query=message.text)
    if not ai_response_text:
        return

    WebClient(token=message.conversation.workspace.bot_token).chat_postMessage(
        channel=message.conversation.slack_channel_id,
        blocks=get_blocks(ai_response_text),
        text=message.text,
        thread_ts=message.slack_message_id,
    )
