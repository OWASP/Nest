"""Slack bot gsoc command."""

from django.utils import timezone

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_START
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
)
from apps.slack.utils import get_gsoc_projects

SUPPORTED_YEAR_START = 2012
SUPPORTED_YEAR_END = 2025
SUPPORTED_YEARS = set(range(SUPPORTED_YEAR_START, SUPPORTED_YEAR_END + 1))
SUPPORTED_ANNOUNCEMENT_YEARS = SUPPORTED_YEARS - {2012, 2013, 2014, 2015, 2016, 2018}

MARCH = 3
now = timezone.now()
gsoc_year = now.year if now.month > MARCH else now.year - 1
projects_url = get_absolute_url("projects")


class Gsoc(CommandBase):
    """Slack bot /gsoc command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        command_text = command["text"].strip()
        template = self.get_template_file()

        if not command_text or command_text in COMMAND_START:
            return template.render(
                mode="general",
                gsoc_channel=OWASP_GSOC_CHANNEL_ID,
                contribute_channel=OWASP_CONTRIBUTE_CHANNEL_ID,
                previous_year=gsoc_year,
                projects_url=projects_url,
                NL=NL,
            )
        if command_text.isnumeric():
            year = int(command_text)
            if year in SUPPORTED_YEARS:
                gsoc_projects = get_gsoc_projects(year)
                projects_list = sorted(gsoc_projects, key=lambda p: p["idx_name"])
                return template.render(
                    mode="year",
                    year=year,
                    projects=projects_list,
                    has_announcement=year in SUPPORTED_ANNOUNCEMENT_YEARS,
                    NL=NL,
                )
            return template.render(
                mode="unsupported_year",
                year=year,
                supported_start=SUPPORTED_YEAR_START,
                supported_end=SUPPORTED_YEAR_END,
                command=self.get_command(),
                NL=NL,
            )
        return template.render(
            mode="invalid", command_text=command_text, command=self.get_command(), NL=NL
        )
