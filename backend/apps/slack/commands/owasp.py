"""Slack bot owasp command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.constants import COMMAND_HELP
from apps.slack.utils import escape, get_text

COMMAND = "/owasp"


def owasp_handler(ack, command, client):
    """Slack /owasp command handler."""
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
        sponsors,
        staff,
        users,
    )

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_tokens = command["text"].split()
    if not command_tokens or command_tokens[0] in COMMAND_HELP:
        blocks = [
            markdown(
                f"• `{COMMAND} board` -- OWASP Global Board information{NL}"
                f"• `{COMMAND} chapters` -- Explore OWASP chapters{NL}"
                f"• `{COMMAND} committees` -- Explore OWASP committees{NL}"
                f"• `{COMMAND} community` -- Explore OWASP community{NL}"
                f"• `{COMMAND} contact` -- Contact OWASP{NL}"
                f"• `{COMMAND} contribute` -- OWASP projects contribution opportunities{NL}"
                f"• `{COMMAND} donate` -- Support OWASP with a donation{NL}"
                f"• `{COMMAND} events` -- Browse OWASP events{NL}"
                f"• `{COMMAND} gsoc` -- Google Summer of Code participants information{NL}"
                f"• `{COMMAND} jobs` -- Check out available job opportunities{NL}"
                f"• `{COMMAND} leaders` -- Chapter and project leaders search{NL}"
                f"• `{COMMAND} news` -- OWASP news{NL}"
                f"• `{COMMAND} projects` -- Explore OWASP projects{NL}"
                f"• `{COMMAND} sponsors` -- Get a list of OWASP sponsors{NL}"
                f"• `{COMMAND} staff` -- OWASP corporate structure{NL}"
                f"• `{COMMAND} users` -- OWASP contributors{NL}"
            ),
        ]
        conversation = client.conversations_open(users=command["user_id"])
        client.chat_postMessage(
            channel=conversation["channel"]["id"], blocks=blocks, text=get_text(blocks)
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
            case "sponsors":
                sponsors.sponsors_handler(ack, command, client)
            case "staff":
                staff.staff_handler(ack, command, client)
            case "users":
                users.users_handler(ack, command, client)
            case _:
                blocks = [
                    markdown(f"*`{COMMAND} {escape(handler)}` is not supported*{NL}"),
                ]
                conversation = client.conversations_open(users=command["user_id"])
                client.chat_postMessage(
                    blocks=blocks,
                    channel=conversation["channel"]["id"],
                    text=get_text(blocks),
                )


if SlackConfig.app:
    owasp_handler = SlackConfig.app.command(COMMAND)(owasp_handler)
