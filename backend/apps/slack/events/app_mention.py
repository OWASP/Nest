"""Slack app mention event handler."""

import contextlib
import logging

from slack_sdk.errors import SlackApiError

from apps.slack.events.event import EventBase
from apps.slack.models import Conversation, Workspace

logger = logging.getLogger(__name__)


class AppMention(EventBase):
    """Handles app mention events when the bot is mentioned in a channel."""

    event_type = "app_mention"

    def handle_event(self, event, client):
        """Handle an incoming app mention event."""
        channel_id = event.get("channel")
        text = event.get("text", "")

        # Check if conversation exists and is enabled
        conversation_exists = Conversation.objects.filter(
            is_nest_bot_assistant_enabled=True,
            slack_channel_id=channel_id,
        ).exists()

        # Auto-create conversation if it doesn't exist (works in all environments)
        if not conversation_exists:
            try:
                auth_info = client.auth_test()
                workspace_id = auth_info.get("team_id")
                workspace, _ = Workspace.objects.get_or_create(
                    slack_workspace_id=workspace_id,
                    defaults={"name": auth_info.get("team", "Unknown")},
                )
                # Try to get channel info to set proper name
                try:
                    channel_info = client.conversations_info(channel=channel_id)
                    channel_name = channel_info.get("channel", {}).get("name", channel_id)
                except SlackApiError:
                    channel_name = channel_id

                conversation, created = Conversation.objects.get_or_create(
                    slack_channel_id=channel_id,
                    workspace=workspace,
                    defaults={
                        "name": channel_name,
                        "is_nest_bot_assistant_enabled": True,
                    },
                )
                if created:
                    logger.info(
                        "Auto-created and enabled conversation",
                        extra={"channel_id": channel_id, "channel_name": channel_name},
                    )
                elif not conversation.is_nest_bot_assistant_enabled:
                    conversation.is_nest_bot_assistant_enabled = True
                    conversation.save(update_fields=["is_nest_bot_assistant_enabled"])
                    logger.info(
                        "Auto-enabled conversation",
                        extra={"channel_id": channel_id},
                    )
                conversation_exists = True
            except Exception as e:
                logger.exception(
                    "Failed to auto-create conversation",
                    extra={"channel_id": channel_id, "error": str(e)},
                )

        if not conversation_exists:
            logger.warning(
                "NestBot AI Assistant is not enabled for this conversation.",
                extra={"channel_id": channel_id},
            )
            # Inform the user that the assistant is not enabled
            try:
                thread_ts = event.get("thread_ts") or event.get("ts")
                client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        "⚠️ NestBot AI Assistant is not enabled for this channel. "
                        "Please contact an administrator to enable it."
                    ),
                    thread_ts=thread_ts,
                )
            except SlackApiError:
                logger.exception("Failed to post message about assistant not being enabled")
            return

        query = text
        for mention in event.get("blocks", []):
            if mention.get("type") == "rich_text":
                for element in mention.get("elements", []):
                    if element.get("type") == "rich_text_section":
                        for text_element in element.get("elements", []):
                            if text_element.get("type") == "text":
                                query = text_element.get("text", "").strip()
                                break

        if not query:
            logger.warning("No query found in app mention")
            return

        logger.info(
            "Handling app mention",
            extra={"channel_id": channel_id, "query": query[:100]},
        )

        thread_ts = event.get("thread_ts") or event.get("ts")
        message_ts = event.get("ts")

        try:
            client.reactions_add(
                channel=channel_id,
                timestamp=message_ts,
                name="eyes",
            )
        except Exception:
            logger.exception("Failed to add reaction to message")

        # Process query in the background
        import django_rq

        from apps.slack.services.message_auto_reply import (
            process_ai_query_async,
        )

        try:
            django_rq.get_queue("ai").enqueue(
                process_ai_query_async,
                query=query,
                channel_id=channel_id,
                message_ts=message_ts,
                thread_ts=thread_ts,
                is_app_mention=True,
            )
        except Exception as e:
            # Remove eyes reaction on enqueue failure
            with contextlib.suppress(SlackApiError):
                client.reactions_remove(
                    channel=channel_id,
                    timestamp=message_ts,
                    name="eyes",
                )

            # Post user-facing error message
            with contextlib.suppress(SlackApiError):
                client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        "⚠️ An error occurred while processing your query. Please try again later."
                    ),
                    thread_ts=thread_ts or message_ts,
                )

            # Log the exception with context for debugging
            logger.exception(
                "Failed to enqueue AI query processing",
                extra={
                    "channel_id": channel_id,
                    "message_ts": message_ts,
                    "thread_ts": thread_ts,
                    "query": query[:100],
                    "error": str(e),
                },
            )
            raise
