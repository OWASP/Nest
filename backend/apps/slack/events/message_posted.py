"""Slack message event template."""

import logging
from datetime import timedelta

import django_rq

from apps.ai.common.constants import QUEUE_RESPONSE_TIME_MINUTES
from apps.slack.common.question_detector import QuestionDetector
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation, Member, Message

logger = logging.getLogger(__name__)


class MessagePosted(EventBase):
    """Handles new messages posted in channels."""

    event_type = "message"
    _bot_user_id = None  # Cache bot user ID to avoid repeated auth_test() calls

    def __init__(self):
        """Initialize MessagePosted event handler."""
        self.question_detector = QuestionDetector()

    def handle_event(self, event, client):
        """Handle an incoming message event."""
        if event.get("subtype") or event.get("bot_id"):
            logger.info("Ignored message due to subtype, bot_id, or thread_ts.")
            return

        if event.get("thread_ts"):
            # filter().update() doesn't raise DoesNotExist, it just returns 0 if no matches
            updated_count = Message.objects.filter(
                slack_message_id=event.get("thread_ts"),
                conversation__slack_channel_id=event.get("channel"),
            ).update(has_replies=True)
            if updated_count == 0:
                logger.debug("Thread message not found for update.")
            return

        # message_posted ignores bot mentions - app_mention handler handles them
        # This handler only processes non-mention messages to avoid duplicate processing
        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")

        # Check if bot is mentioned in the message text or blocks
        bot_mentioned = False
        try:
            # Cache bot_user_id to avoid repeated auth_test() calls
            if MessagePosted._bot_user_id is None:
                bot_info = client.auth_test()
                MessagePosted._bot_user_id = bot_info.get("user_id")
            bot_user_id = MessagePosted._bot_user_id
            if bot_user_id:
                # Check text for mention format: <@BOT_USER_ID>
                if f"<@{bot_user_id}>" in text:
                    bot_mentioned = True
                else:
                    # Check blocks for user mentions
                    for block in event.get("blocks", []):
                        if block.get("type") == "rich_text":
                            for element in block.get("elements", []):
                                if element.get("type") == "rich_text_section":
                                    for text_element in element.get("elements", []):
                                        if (
                                            text_element.get("type") == "user"
                                            and text_element.get("user_id") == bot_user_id
                                        ):
                                            bot_mentioned = True
                                            break
                                    if bot_mentioned:
                                        break
                            if bot_mentioned:
                                break
        except Exception:
            logger.warning("Could not check bot mention, skipping auto-reply to be safe.")
            return

        # Skip messages where bot is mentioned - app_mention handler will process them
        if bot_mentioned:
            logger.debug(
                "Bot mentioned in message, skipping - app_mention handler will process it."
            )
            return

        try:
            conversation = Conversation.objects.get(
                slack_channel_id=channel_id,
                is_nest_bot_assistant_enabled=True,
            )
        except Conversation.DoesNotExist:
            logger.warning("Conversation not found or assistant not enabled.")
            return

        is_owasp = self.question_detector.is_owasp_question(text)
        logger.info(
            "Question detector result",
            extra={
                "channel_id": channel_id,
                "is_owasp": is_owasp,
                "text": text[:200],
            },
        )
        if not is_owasp:
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

        logger.info(
            "Enqueueing AI reply generation",
            extra={
                "message_id": message.id,
                "channel_id": channel_id,
                "delay_minutes": QUEUE_RESPONSE_TIME_MINUTES,
            },
        )
        # Import here to avoid AppRegistryNotReady error (lazy import)
        from apps.slack.services.message_auto_reply import (
            generate_ai_reply_if_unanswered,
        )

        django_rq.get_queue("ai").enqueue_in(
            timedelta(minutes=QUEUE_RESPONSE_TIME_MINUTES),
            generate_ai_reply_if_unanswered,
            message.id,
        )
