"""Slack bot projects command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers import EntityPresentation, projects_blocks

COMMAND = "/projects"


def projects_handler(ack, command, client):
    """Slack /projects command handler."""
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"].strip()
    blocks = projects_blocks(
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


handler = projects_handler
if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(projects_handler)
