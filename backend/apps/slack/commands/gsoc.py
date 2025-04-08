"""Slack bot gsoc command."""

from django.utils import timezone

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_START
from apps.slack.constants import (
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
)
from apps.slack.utils import get_gsoc_projects

SUPPORTED_YEAR_START = 2012
SUPPORTED_YEAR_END = 2025
SUPPORTED_YEARS = set(range(SUPPORTED_YEAR_START, SUPPORTED_YEAR_END + 1))
SUPPORTED_ANNOUNCEMENT_YEARS = SUPPORTED_YEARS - {2012, 2013, 2014, 2015, 2016, 2018}

MARCH = 3
projects_url = get_absolute_url("projects")


class Gsoc(CommandBase):
    """Slack bot /gsoc command."""

    def get_template_context(self, command):
        """Get the template context."""
        now = timezone.now()
        gsoc_year = now.year if now.month > MARCH else now.year - 1
        command_text = command["text"].strip()
        context = super().get_template_context(command)
        template_context = {"mode": "", "command": self.get_command()}

        if not command_text or command_text in COMMAND_START:
            template_context.update(
                {
                    "mode": "general",
                    "gsoc_channel": OWASP_GSOC_CHANNEL_ID,
                    "contribute_channel": OWASP_CONTRIBUTE_CHANNEL_ID,
                    "previous_year": gsoc_year,
                    "projects_url": projects_url,
                    "feedback_channel": OWASP_PROJECT_NEST_CHANNEL_ID,
                    "nest_bot_name": NEST_BOT_NAME,
                }
            )
        elif command_text.isnumeric():
            year = int(command_text)
            if year in SUPPORTED_YEARS:
                template_context.update(
                    {
                        "mode": "year",
                        "year": year,
                        "projects": sorted(get_gsoc_projects(year), key=lambda p: p["idx_name"]),
                        "has_announcement": year in SUPPORTED_ANNOUNCEMENT_YEARS,
                    }
                )
            else:
                template_context.update(
                    {
                        "mode": "unsupported_year",
                        "year": year,
                        "supported_start": SUPPORTED_YEAR_START,
                        "supported_end": SUPPORTED_YEAR_END,
                    }
                )
        else:
            template_context.update(
                {
                    "mode": "invalid",
                    "command_text": command_text,
                }
            )

        context.update(template_context)
        return context
