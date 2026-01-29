"""Slack bot AI command."""

from apps.slack.commands.command import CommandBase


class Ai(CommandBase):
    """Slack bot /ai command."""

    def handler(self, ack, command, client):
        """Handle the Slack /ai command."""
        ack()

        query = command.get("text", "").strip()
        if not query:
            return

        channel_id = command.get("channel_id")
        user_id = command.get("user_id")

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

        django_rq.get_queue("ai").enqueue(
            process_ai_query_async,
            query=query,
            channel_id=channel_id,
            message_ts=None, # No TS to react to initially
            thread_ts=None,
            is_app_mention=False,
            user_id=user_id,
        )
