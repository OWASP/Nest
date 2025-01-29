"""Slack bot users command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/users"


def users_handler(ack, command, client):
    """Slack /users command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(f"Please visit <https://nest.owasp.dev/users/users/|OWASP users> page{NL}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    users_handler = SlackConfig.app.command(COMMAND)(users_handler)
