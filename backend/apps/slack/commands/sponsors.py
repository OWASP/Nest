"""Slack bot sponsors command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.sponsor import get_blocks
from apps.slack.common.presentation import EntityPresentation

COMMAND = "/sponsors"


def sponsors_handler(ack, command, client):
    """Slack /sponsors command handler."""
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"].strip()
    blocks = get_blocks(
        search_query=search_query,
        limit=10,
        presentation=EntityPresentation(
            include_feedback=True,
            include_metadata=True,
            include_pagination=False,
            include_timestamps=True,
            name_truncation=80,
            summary_truncation=300,
        ),
    )

    fallback_text = "OWASP Sponsors Information"
    if search_query:
        fallback_text += f" - Search results for: {search_query}"

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        channel=conversation["channel"]["id"], blocks=blocks, text=fallback_text
    )


if SlackConfig.app:
    sponsors_handler = SlackConfig.app.command(COMMAND)(sponsors_handler)
