"""Slack bot gsoc command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.constants import COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import get_text

COMMAND = "/gsoc"

SUPPORTED_YEAR_START = 2012
SUPPORTED_YEAR_END = 2025
SUPPORTED_YEARS = set(range(SUPPORTED_YEAR_START, SUPPORTED_YEAR_END + 1))
SUPPORTED_ANNOUNCEMENT_YEARS = SUPPORTED_YEARS - {2012, 2013, 2014, 2015, 2016, 2018}


def gsoc_handler(ack, command, client):
    """Slack /gsoc command handler."""
    from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS
    from apps.slack.utils import get_gsoc_projects

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()

    if not command_text or command_text in COMMAND_START:
        blocks = [
            *GSOC_GENERAL_INFORMATION_BLOCKS,
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ]
    elif command_text.isnumeric():
        year = int(command_text)
        if year in SUPPORTED_YEARS:
            gsoc_projects = get_gsoc_projects(year)
            gsoc_projects_markdown = f"{NL}".join(
                f"  • <{gp['idx_url']}|{gp['idx_name']}>"
                for gp in sorted(gsoc_projects, key=lambda p: p["idx_name"])
            )
            additional_info = []
            blocks = [
                markdown(f"*GSoC {year} projects:*{2*NL}{gsoc_projects_markdown}"),
            ]
            if year in SUPPORTED_ANNOUNCEMENT_YEARS:
                additional_info.append(
                    f"  • <https://owasp.org/www-community/initiatives/gsoc/gsoc{year}|"
                    f"GSoC {year} announcement>{NL}"
                )

            additional_info.append(
                f"  • <https://owasp.org/www-community/initiatives/gsoc/gsoc{year}ideas|"
                f"GSoC {year} ideas>"
            )
            blocks.append(
                markdown(
                    f"Additional information:{NL}{''.join(additional_info)}",
                ),
            )
        else:
            blocks = [
                markdown(
                    f"Year {year} is not supported. Supported years: "
                    f"{SUPPORTED_YEAR_START}-{SUPPORTED_YEAR_END}, "
                    f"e.g. `{COMMAND} {SUPPORTED_YEAR_END}`"
                )
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
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    gsoc_handler = SlackConfig.app.command(COMMAND)(gsoc_handler)
