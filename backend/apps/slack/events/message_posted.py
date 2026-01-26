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
        # Ignore bot messages
        if event.get("bot_id"):
            logger.info("Ignoring bot message.")
            return

        # Allow file_share subtype (messages with images), ignore others
        if event.get("subtype") and event.get("subtype") != "file_share":
            logger.info("Ignoring message with subtype: %s", event.get("subtype"))
            return

        # Update parent message if this is a thread reply
        if event.get("thread_ts"):
            updated = Message.objects.filter(
                slack_message_id=event.get("thread_ts"),
                conversation__slack_channel_id=event.get("channel"),
            ).update(has_replies=True)
            if not updated:
                logger.info(
                    "Parent message for thread_ts %s not found in thread reply.",
                    event.get("thread_ts"),
                )
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
            logger.info("Conversation not found or bot not enabled for channel: %s", channel_id)
            return

        # Check if message has valid images - only bypass question detector for valid images
        from apps.slack.services.image_extraction import (
            extract_images_then_maybe_reply,
            is_valid_image_file,
        )

        image_files = [
            f
            for f in event.get("files", [])
            if f.get("mimetype", "").startswith("image/") and is_valid_image_file(f)
        ][:3]

        # For text-only messages or messages without valid images, use question detector
        if not image_files and not self.question_detector.is_owasp_question(text):
            logger.info("Question detector rejected message")
            return

        try:
            author = Member.objects.get(
                slack_user_id=user_id,
                workspace=conversation.workspace,
            )
        except Member.DoesNotExist:
            user_info = client.users_info(user=user_id)
            author = Member.update_data(
                user_info["user"],
                conversation.workspace,
                save=True,
            )
            logger.info("Created new member for user_id %s", user_id)

        message = Message.update_data(
            data=event,
            conversation=conversation,
            author=author,
            save=True,
        )

        # Handle messages with valid images
        if image_files:
            logger.info(
                "Queueing image extraction for message %s with %s image(s)",
                message.id,
                len(image_files),
            )
            django_rq.get_queue("ai").enqueue(
                extract_images_then_maybe_reply,
                message.id,
                image_files,
            )
        else:
            logger.info("Queueing AI reply for message %s", message.id)
            django_rq.get_queue("ai").enqueue_in(
                timedelta(minutes=QUEUE_RESPONSE_TIME_MINUTES),
                generate_ai_reply_if_unanswered,
                message.id,
            )
