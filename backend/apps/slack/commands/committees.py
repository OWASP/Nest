"""Slack bot committees command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers import EntityPresentation, committees_blocks

COMMAND = "/committees"


def committees_handler(ack, command, client):
    """Refactored Slack /committees command handler."""
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"].strip()
    blocks = committees_blocks(
        search_query=search_query,
        limit=10,
        presentation=EntityPresentation(
            name_truncation=80,
            summary_truncation=300,
            include_feedback=True,
            include_timestamps=True,
            include_metadata=True,
        ),
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(committees_handler)
