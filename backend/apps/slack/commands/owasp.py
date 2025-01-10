"""Slack bot owasp command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_HELP
from apps.slack.utils import escape

COMMAND = "/owasp"


def handler(ack, command, client):
    """Slack /owasp command handler."""
    from apps.slack.commands import committees, contribute, gsoc, projects

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_tokens = command["text"].split()
    if not command_tokens or command_tokens[0] in COMMAND_HELP:
        blocks = [
            markdown(
                f"• `{COMMAND} contribute` -- OWASP projects contribution opportunities{NL}"
                f"• `{COMMAND} gsoc` -- Google Summer of Code participants information{NL}"
                f"• `{COMMAND} projects` -- Explore OWASP projects{NL}"
                f"• `{COMMAND} committees` -- Explore OWASP committees{NL}"
            ),
        ]
        conversation = client.conversations_open(users=command["user_id"])
        client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)
    else:
        handler = command_tokens[0].strip().lower()
        command["text"] = " ".join(command_tokens[1:]).strip()
        match handler:
            case "contribute":
                contribute.handler(ack, command, client)
            case "gsoc":
                gsoc.handler(ack, command, client)
            case "projects":
                projects.handler(ack, command, client)
            case "committees":
                committees.handler(ack, command, client)
            case _:
                blocks = [
                    markdown(f"*`{COMMAND} {escape(handler)}` is not supported*{NL}"),
                ]
                conversation = client.conversations_open(users=command["user_id"])
                client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
