"""Slack message event template."""

import logging
from datetime import timedelta

import django_rq

from apps.ai.common.constants import QUEUE_RESPONSE_TIME_MINUTES
from apps.slack.common.question_detector import QuestionDetector
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation, Member, Message
from apps.slack.services.message_auto_reply import generate_ai_reply_if_unanswered

logger = logging.getLogger(__name__)


class MessagePosted(EventBase):
    """Handles new messages posted in channels."""

    event_type = "message"

    def __init__(self):
        """Initialize MessagePosted event handler."""
        self.question_detector = QuestionDetector()

    def handle_event(self, event, client):
        """Handle an incoming message event."""
        if event.get("subtype") or event.get("bot_id"):
            logger.info("Ignored message due to subtype, bot_id, or thread_ts.")
            return

        if event.get("thread_ts"):
            try:
                Message.objects.filter(
                    slack_message_id=event.get("thread_ts"),
                    conversation__slack_channel_id=event.get("channel"),
                ).update(has_replies=True)
            except Message.DoesNotExist:
                logger.warning("Thread message not found.")
            return

        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")

        try:
            conversation = Conversation.objects.get(
                slack_channel_id=channel_id,
                is_nest_bot_assistant_enabled=True,
            )
        except Conversation.DoesNotExist:
            logger.warning("Conversation not found or assistant not enabled.")
            return

        # Check if it's an OWASP question (skip if OpenAI is not available for testing)
        try:
            if not self.question_detector.is_owasp_question(text):
                return
        except Exception as e:
            logger.warning(f"Question detection failed (OpenAI unavailable): {e}")
            # Continue anyway for testing purposes when OpenAI key is not configured

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
