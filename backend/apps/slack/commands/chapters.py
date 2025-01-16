"""Slack bot chapter command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.constants import COMMAND_HELP, COMMAND_START
from apps.slack.common.handlers import EntityPresentation, chapters_blocks

COMMAND = "/chapters"


def chapters_handler(ack, command, client):
    """Refactored Slack /chapters command handler."""
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()

    if command_text in COMMAND_HELP:
        blocks = [
            markdown(
                f"*Available Commands:*{NL}"
                f"• `/chapters` - recent chapters{NL}"
                f"• `/chapters [search term]` - Search for specific chapters{NL}"
                f"• `/chapters [region]` - Search for specific region chapters{NL}"
            ),
        ]
    else:
        search_query = "" if command_text in COMMAND_START else command_text
        blocks = chapters_blocks(
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
    handler = SlackConfig.app.command(COMMAND)(chapters_handler)
