"""Slack bot gsoc command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, NL

COMMAND = "/gsoc"


def handler(ack, command, client):
    """Slack /gsoc command handler."""
    from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()
    if not command_text or command_text in COMMAND_START:
        blocks = [
            *GSOC_GENERAL_INFORMATION_BLOCKS,
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ]
    else:
        blocks = [
            markdown(
                f"*`{COMMAND} {command_text}` is not supported*{NL}"
                if command_text
                else f"*`{COMMAND}` is not supported*{NL}"
            ),
        ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
