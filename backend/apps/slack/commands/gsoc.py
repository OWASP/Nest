"""Slack bot gsoc command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_START
from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, NL

COMMAND = "/gsoc"
SUPPORTED_YEARS = set(range(2020, 2025))  # 2020-2024


def handler(ack, command, client):
    """Slack /gsoc command handler."""
    from apps.owasp.models.project import Project

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
            gsoc_projects = Project.get_gsoc_projects(year)
            gsoc_projects_markwown = f"{NL}".join(
                f"  • <{gp.nest_url}|{gp.owasp_name}>"
                for gp in sorted(gsoc_projects, key=lambda p: p.owasp_name)
            )
            blocks = [
                markdown(f"*GSoC {year} projects:*{2*NL}{gsoc_projects_markwown}"),
                markdown(
                    f"Additional information:{NL}"
                    f"  • <https://owasp.org/www-community/initiatives/gsoc/gsoc{year}|"
                    f"GSoC {year} announcement>{NL}"
                    f"  • <https://owasp.org/www-community/initiatives/gsoc/gsoc{year}ideas|"
                    f"GSoC {year} ideas>"
                ),
            ]
        else:
            blocks = [
                markdown(
                    f"Year {year} is not supported. Supported years: 2020-2024, "
                    f"e.g. `{COMMAND} {sorted(SUPPORTED_YEARS)[-1]}`"
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
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
