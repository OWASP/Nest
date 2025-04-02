"""Slack bot owasp command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.constants import COMMAND_HELP
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text

COMMAND = "/owasp"


def owasp_handler(ack, command, client):
    """Handle the Slack /owasp command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    from apps.slack.commands import (
        board,
        chapters,
        committees,
        community,
        contact,
        contribute,
        donate,
        events,
        gsoc,
        jobs,
        leaders,
        news,
        projects,
        sponsor,
        sponsors,
        staff,
        users,
    )

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    template = env.get_template("owasp.txt")

    command_tokens = command["text"].split()
    if not command_tokens or command_tokens[0] in COMMAND_HELP:
        context = {
            "help": True,
            "command": COMMAND,
        }
        rendered_text = template.render(context)
        blocks = [markdown(rendered_text)]
        conversation = client.conversations_open(users=command["user_id"])
        client.chat_postMessage(
            channel=conversation["channel"]["id"],
            blocks=blocks,
            text=get_text(blocks),
        )
    else:
        handler = command_tokens[0].strip().lower()
        command["text"] = " ".join(command_tokens[1:]).strip()
        match handler:
            case "board":
                board.board_handler(ack, command, client)
            case "chapters":
                chapters.chapters_handler(ack, command, client)
            case "committees":
                committees.committees_handler(ack, command, client)
            case "community":
                community.community_handler(ack, command, client)
            case "contact":
                contact.contact_handler(ack, command, client)
            case "contribute":
                contribute.contribute_handler(ack, command, client)
            case "donate":
                donate.donate_handler(ack, command, client)
            case "events":
                events.events_handler(ack, command, client)
            case "gsoc":
                gsoc.gsoc_handler(ack, command, client)
            case "jobs":
                jobs.jobs_handler(ack, command, client)
            case "leaders":
                leaders.leaders_handler(ack, command, client)
            case "news":
                news.news_handler(ack, command, client)
            case "projects":
                projects.projects_handler(ack, command, client)
            case "sponsor":
                sponsor.sponsor_handler(ack, command, client)
            case "sponsors":
                sponsors.sponsors_handler(ack, command, client)
            case "staff":
                staff.staff_handler(ack, command, client)
            case "users":
                users.users_handler(ack, command, client)
            case _:
                context = {"help": False, "command": COMMAND, "handler": handler}
                rendered_text = template.render(context)
                blocks = [
                    markdown(rendered_text),
                ]
                conversation = client.conversations_open(users=command["user_id"])
                client.chat_postMessage(
                    blocks=blocks,
                    channel=conversation["channel"]["id"],
                    text=get_text(blocks),
                )


if SlackConfig.app:
    owasp_handler = SlackConfig.app.command(COMMAND)(owasp_handler)
