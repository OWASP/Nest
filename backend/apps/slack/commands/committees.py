"""Slack bot committees command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.committees import get_blocks
from apps.slack.common.presentation import EntityPresentation
from apps.slack.utils import get_text

COMMAND = "/committees"


def committees_handler(ack, command, client):
    """Slack /committees command handler."""
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
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    committees_handler = SlackConfig.app.command(COMMAND)(committees_handler)
