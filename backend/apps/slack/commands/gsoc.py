"""Slack bot gsoc command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, NL

COMMAND = "/gsoc"
SUPPORTED_YEARS = {2020, 2021, 2022, 2023, 2024}


def get_gsoc_projects_by_year(year):
    """Get GSOC projects for a specific year using search."""
    from apps.owasp.models.project import Project

    return Project.get_gsoc_projects(
        year,
        attributes=["name", "related_urls"],
        limit=100,
    )


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
        try:
            year = int(command_text)
            if year in SUPPORTED_YEARS:
                results = get_gsoc_projects_by_year(year)
                projects_list = "\n".join(
                    f"• <{hit['idx_url']}|{hit['idx_name']}>" for hit in results["hits"]
                )
                blocks = [markdown(f"GSoC {year} Projects:\n\n{projects_list}")]
            else:
                blocks = [markdown("Usage: `/gsoc [year]`\nValid years: 2020-2024")]
        except ValueError:
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
