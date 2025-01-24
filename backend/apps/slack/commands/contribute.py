"""Slack bot contribute command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.contribute import get_blocks
from apps.slack.common.presentation import EntityPresentation

COMMAND = "/contribute"


def contribute_handler(ack, command, client):
    """Slack /contribute command handler."""
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
    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    contribute_handler = SlackConfig.app.command(COMMAND)(contribute_handler)
