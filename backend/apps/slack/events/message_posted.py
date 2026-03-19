"""Slack message event template."""

import logging
from datetime import timedelta

import django_rq
from slack_sdk.errors import SlackApiError

from apps.ai.common.constants import QUEUE_RESPONSE_TIME_MINUTES
from apps.slack.common.question_detector import QuestionDetector
from apps.slack.events.event import EventBase
from apps.slack.models import Conversation, Member, Message

logger = logging.getLogger(__name__)


class MessagePosted(EventBase):
    """Handles new messages posted in channels."""

    event_type = "message"
    _bot_user_id_by_team: dict[str, str] = {}

    def __init__(self):
        """Initialize MessagePosted event handler."""
        self.question_detector = QuestionDetector()

    def handle_event(self, event, client):  # noqa: PLR0911
        """Handle an incoming message event."""
        if event.get("subtype") or event.get("bot_id"):
            logger.info("Ignored message due to subtype or bot_id.")
            return

        if event.get("thread_ts"):
            updated_count = Message.objects.filter(
                slack_message_id=event.get("thread_ts"),
                conversation__slack_channel_id=event.get("channel"),
            ).update(has_replies=True)
            if updated_count == 0:
                logger.debug("Thread message not found for update.")
            return

        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")

        try:
            conversation = Conversation.objects.select_related("workspace").get(
                slack_channel_id=channel_id,
                is_nest_bot_assistant_enabled=True,
            )
        except Conversation.DoesNotExist:
            logger.warning("Conversation not found or assistant not enabled.")
            return

        bot_mentioned = False
        team_id = conversation.workspace.slack_workspace_id
        bot_user_id = MessagePosted._bot_user_id_by_team.get(team_id)

        if bot_user_id is None:
            try:
                bot_info = client.auth_test()
                auth_team_id = bot_info.get("team_id")
                bot_user_id = bot_info.get("user_id")
                if auth_team_id == team_id:
                    MessagePosted._bot_user_id_by_team[team_id] = bot_user_id
                else:
                    logger.warning(
                        "Team ID mismatch between conversation and auth_test",
                        extra={"conversation_team_id": team_id, "auth_team_id": auth_team_id},
                    )
                    MessagePosted._bot_user_id_by_team[team_id] = bot_user_id
                    MessagePosted._bot_user_id_by_team[auth_team_id] = bot_user_id
            except SlackApiError:
                logger.exception(
                    "Failed to get bot user ID from Slack API",
                    extra={"channel_id": channel_id, "team_id": team_id},
                )
                bot_user_id = None

        if bot_user_id:
            try:
                if f"<@{bot_user_id}>" in text:
                    bot_mentioned = True
                else:
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
            except (KeyError, TypeError, ValueError) as e:
                logger.warning(
                    "Error parsing event for bot mention check; continuing as non-mention",
                    extra={
                        "channel_id": channel_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                bot_mentioned = False

        if bot_mentioned:
            logger.debug("Bot mentioned in message; app_mention handler will process it.")
            return

        if not self.question_detector.is_owasp_question(text):
            return

        try:
            author = Member.objects.get(slack_user_id=user_id, workspace=conversation.workspace)
        except Member.DoesNotExist:
            try:
                user_info = client.users_info(user=user_id)
                author = Member.update_data(user_info["user"], conversation.workspace, save=True)
                logger.info("Created new member")
            except SlackApiError:
                logger.exception(
                    "Failed to fetch user info from Slack API",
                    extra={"channel_id": channel_id, "user_id": user_id},
                )
                return
            except (KeyError, TypeError) as e:
                logger.warning(
                    "Unexpected response structure from users_info",
                    extra={"user_id": user_id, "error": str(e)},
                )
                return

        message = Message.update_data(
            data=event, conversation=conversation, author=author, save=True
        )

        from apps.slack.services.message_auto_reply import (
            generate_ai_reply_if_unanswered,
        )

        django_rq.get_queue("ai").enqueue_in(
            timedelta(minutes=QUEUE_RESPONSE_TIME_MINUTES),
            generate_ai_reply_if_unanswered,
            message.id,
        )
