"""Slack message event handler for OWASP NestBot."""

import logging
from datetime import timedelta

import django_rq

from apps.ai.common.constants import QUEUE_RESPONSE_TIME_MINUTES
from apps.slack.common.handlers.ai import get_dm_blocks
from apps.slack.common.question_detector import QuestionDetector
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation, Member, Message, Workspace
from apps.slack.services.message_auto_reply import generate_ai_reply_if_unanswered

logger = logging.getLogger(__name__)


class MessagePosted(EventBase):
    """Handles new messages posted in channels or direct messages."""

    event_type = "message"

    def __init__(self):
        """Initialize MessagePosted event handler."""
        self.question_detector = QuestionDetector()

    def handle_event(self, event, client):
        """Handle incoming Slack message events."""
        if event.get("subtype") or event.get("bot_id"):
            logger.info("Ignored message due to subtype or bot_id.")
            return

        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")
        channel_type = event.get("channel_type")

        if channel_type == "im":
            self.handle_dm(event, client, channel_id, user_id, text)
            return

        if event.get("thread_ts"):
            try:
                Message.objects.filter(
                    slack_message_id=event.get("thread_ts"),
                    conversation__slack_channel_id=channel_id,
                ).update(has_replies=True)
            except Message.DoesNotExist:
                logger.warning("Thread message not found.")
            return

        try:
            conversation = Conversation.objects.get(
                slack_channel_id=channel_id,
                is_nest_bot_assistant_enabled=True,
            )
        except Conversation.DoesNotExist:
            logger.warning("Conversation not found or assistant not enabled.")
            return

        if not self.question_detector.is_owasp_question(text):
            return

        try:
            author = Member.objects.get(slack_user_id=user_id, workspace=conversation.workspace)
        except Member.DoesNotExist:
            user_info = client.users_info(user=user_id)
            author = Member.update_data(user_info["user"], conversation.workspace, save=True)
            logger.info("Created new member")

        message = Message.update_data(
            data=event, conversation=conversation, author=author, save=True
        )

        django_rq.get_queue("ai").enqueue_in(
            timedelta(minutes=QUEUE_RESPONSE_TIME_MINUTES),
            generate_ai_reply_if_unanswered,
            message.id,
        )

    def handle_dm(self, event, client, channel_id, user_id, text):
        """Handle direct messages with NestBot (DMs)."""
        workspace_id = event.get("team")
        channel_info = client.conversations_info(channel=channel_id)

        try:
            workspace = Workspace.objects.get(slack_workspace_id=workspace_id)
        except Workspace.DoesNotExist:
            logger.exception("Workspace not found for DM.")
            return

        Conversation.update_data(channel_info["channel"], workspace)

        try:
            Member.objects.get(slack_user_id=user_id, workspace=workspace)
        except Member.DoesNotExist:
            user_info = client.users_info(user=user_id)
            Member.update_data(user_info["user"], workspace, save=True)
            logger.info("Created new member for DM")

        thread_ts = event.get("thread_ts")

        try:
            response_blocks = get_dm_blocks(text, workspace_id, channel_id)
            if response_blocks:
                client.chat_postMessage(
                    channel=channel_id,
                    blocks=response_blocks,
                    text=text,
                    thread_ts=thread_ts,
                )

        except Exception:
            logger.exception("Error processing DM")
            client.chat_postMessage(
                channel=channel_id,
                text=(
                    "I'm sorry, I'm having trouble processing your message right now. "
                    "Please try again later."
                ),
                thread_ts=thread_ts,
            )
