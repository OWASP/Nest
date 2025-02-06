"""Slack bot board command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import get_text

COMMAND = "/board"


def board_handler(ack, command, client):
    """Slack /board command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(f"Please visit <https://owasp.org/www-board/|Global board> page{NL}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    board_handler = SlackConfig.app.command(COMMAND)(board_handler)
