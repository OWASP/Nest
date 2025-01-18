"""Slack bot projects command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.common.handlers.projects import projects_blocks
from apps.slack.common.presentation import EntityPresentation

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
            include_feedback=True,
            include_metadata=True,
            include_timestamps=True,
            name_truncation=80,
            summary_truncation=300,
        ),
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(projects_handler)
