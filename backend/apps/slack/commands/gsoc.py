"""Slack bot gsoc command."""

from django.conf import settings
from django.utils import timezone

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.constants import COMMAND_START
from apps.slack.constants import (
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
)
from apps.slack.template_system.loader import env
from apps.slack.utils import get_gsoc_projects, get_text

COMMAND = "/gsoc"

SUPPORTED_YEAR_START = 2012
SUPPORTED_YEAR_END = 2025
SUPPORTED_YEARS = set(range(SUPPORTED_YEAR_START, SUPPORTED_YEAR_END + 1))
SUPPORTED_ANNOUNCEMENT_YEARS = SUPPORTED_YEARS - {2012, 2013, 2014, 2015, 2016, 2018}

SEPTEMBER = 9
now = timezone.now()
previous_gsoc_year = now.year if now.month > SEPTEMBER else now.year - 1
projects_url = get_absolute_url("projects")


def gsoc_handler(ack, command, client):
    """Handle the Slack /gsoc command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()
    template = env.get_template("gsoc.txt")
    blocks = []

    if not command_text or command_text in COMMAND_START:
        rendered_text = template.render(
            mode="general",
            gsoc_channel=OWASP_GSOC_CHANNEL_ID,
            contribute_channel=OWASP_CONTRIBUTE_CHANNEL_ID,
            previous_year=previous_gsoc_year,
            projects_url=projects_url,
            NL=NL,
        )
        blocks.append(markdown(rendered_text.strip()))

        feedback_template = env.get_template("feedback.txt")
        feedback_rendered_text = feedback_template.render(
            nest_bot_name=NEST_BOT_NAME,
            feedback_channel=OWASP_PROJECT_NEST_CHANNEL_ID,
        )
        blocks.append(markdown(feedback_rendered_text.strip()))
    elif command_text.isnumeric():
        year = int(command_text)
        if year in SUPPORTED_YEARS:
            gsoc_projects = get_gsoc_projects(year)
            projects_list = sorted(gsoc_projects, key=lambda p: p["idx_name"])
            rendered_text = template.render(
                mode="year",
                year=year,
                projects=projects_list,
                has_announcement=year in SUPPORTED_ANNOUNCEMENT_YEARS,
                NL=NL,
            )
            for section in rendered_text.split("{{ SECTION_BREAK }}"):
                cleaned_section = section.strip()
                if cleaned_section:
                    blocks.append(markdown(cleaned_section))
        else:
            rendered_text = template.render(
                mode="unsupported_year",
                year=year,
                supported_start=SUPPORTED_YEAR_START,
                supported_end=SUPPORTED_YEAR_END,
                command=COMMAND,
                NL=NL,
            )
            blocks.append(markdown(rendered_text.strip()))
    else:
        rendered_text = template.render(
            mode="invalid", command_text=command_text, command=COMMAND, NL=NL
        )
        blocks.append(markdown(rendered_text.strip()))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    gsoc_handler = SlackConfig.app.command(COMMAND)(gsoc_handler)
