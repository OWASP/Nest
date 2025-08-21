"""Slack message event template."""

import logging
from datetime import timedelta

import django_rq

from apps.slack.common.question_detector import QuestionDetector
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation, Member, Message
from apps.slack.services.task import generate_ai_reply_if_unanswered

logger = logging.getLogger(__name__)


class MessagePosted(EventBase):
    """Handles new messages posted in channels."""

    event_type = "message"

    def __init__(self):
        """Initialize MessagePosted event handler."""
        self.question_detector = QuestionDetector()

    def handle_event(self, event, client):
        """Handle an incoming message event."""
        if event.get("subtype") or event.get("bot_id") or event.get("thread_ts"):
            logger.info("Ignored message due to subtype, bot_id, or thread_ts.")
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

        if not self.question_detector.is_owasp_question(text):
            return

        try:
            author = Member.objects.get(slack_user_id=user_id, workspace=conversation.workspace)
            message = Message.update_data(
                data=event, conversation=conversation, author=author, save=True
            )

            django_rq.get_queue("default").enqueue_in(
                timedelta(minutes=1), generate_ai_reply_if_unanswered, message.id
            )

        except Member.DoesNotExist:
            logger.warning("Could not find Member")
            return
