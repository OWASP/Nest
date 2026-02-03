"""Slack bot AI command."""

import logging

from slack_sdk.errors import SlackApiError

from apps.slack.commands.command import CommandBase

logger = logging.getLogger(__name__)


class Ai(CommandBase):
    """Slack bot /ai command."""

    def handler(self, ack, command, client):
        """Handle the Slack /ai command."""
        ack()

        channel_id = command.get("channel_id")
        user_id = command.get("user_id")

        query = command.get("text", "").strip()
        if not query:
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=(
                        "Usage: `/ai <your question>` - "
                        "Ask NestBot a question to get an AI-powered response."
                    ),
                )
            except SlackApiError:
                logger.exception(
                    "Failed to post ephemeral usage hint",
                    extra={"channel_id": channel_id, "user_id": user_id},
                )
            return

        # Slash commands don't have a message TS until we post something,
        # but we can add reactions to the last message or just use the trigger_id
        # However, it's better to just post an ephemeral message or send a message to the channel.

        # For /ai, we usually want to post to the channel.
        # But Slack doesn't provide a message TS for the command itself.
        # We'll just post a placeholder or just wait for the async reply.

        # Let's post an ephemeral "Thinking..." message or just go async.
        import django_rq

        from apps.slack.services.message_auto_reply import (
            process_ai_query_async,
        )

        try:
            django_rq.get_queue("ai").enqueue(
                process_ai_query_async,
                query=query,
                channel_id=channel_id,
                message_ts=None,  # No TS to react to initially
                thread_ts=None,
                is_app_mention=False,
                user_id=user_id,
            )
        except Exception as e:
            # Post user-facing error message via ephemeral (slash command pattern)
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=(
                        "⚠️ An error occurred while processing your query. Please try again later."
                    ),
                )
            except SlackApiError:
                logger.warning(
                    "Failed to post ephemeral error message to user",
                    extra={"channel_id": channel_id, "user_id": user_id},
                )

            # Log the exception with context for debugging
            logger.exception(
                "Failed to enqueue AI query processing for /ai command",
                extra={
                    "channel_id": channel_id,
                    "user_id": user_id,
                    "query": query[:100],
                    "error": str(e),
                },
            )
