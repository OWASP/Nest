"""Slack bot gsoc command."""

from django.utils import timezone

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_START
from apps.slack.common.gsoc import MARCH
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
)

SUPPORTED_YEAR_START = 2012
SUPPORTED_YEAR_END = 2025
SUPPORTED_YEARS = set(range(SUPPORTED_YEAR_START, SUPPORTED_YEAR_END + 1))
SUPPORTED_ANNOUNCEMENT_YEARS = SUPPORTED_YEARS - {2012, 2013, 2014, 2015, 2016, 2018}


class Gsoc(CommandBase):
    """Slack bot /gsoc command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        from apps.owasp.utils.gsoc import get_gsoc_projects

        now = timezone.now()
        gsoc_year = now.year if now.month > MARCH else now.year - 1
        command_text = command["text"].strip()
        context = {}

        if not command_text or command_text in COMMAND_START:
            context.update(
                {
                    "CONTRIBUTE_CHANNEL_ID": OWASP_CONTRIBUTE_CHANNEL_ID,
                    "GSOC_CHANNEL_ID": OWASP_GSOC_CHANNEL_ID,
                    "MODE": "GENERAL",
                    "PREVIOUS_YEAR": gsoc_year,
                    "PROJECTS_URL": get_absolute_url("/projects"),
                }
            )
        elif command_text.isnumeric():
            year = int(command_text)
            if year in SUPPORTED_YEARS:
                context.update(
                    {
                        "HAS_ANNOUNCEMENT": year in SUPPORTED_ANNOUNCEMENT_YEARS,
                        "MODE": "YEAR",
                        "PROJECTS": sorted(get_gsoc_projects(year), key=lambda p: p["name"]),
                        "YEAR": year,
                    }
                )
            else:
                context.update(
                    {
                        "MODE": "UNSUPPORTED_YEAR",
                        "SUPPORTED_YEAR_END": SUPPORTED_YEAR_END,
                        "SUPPORTED_YEAR_START": SUPPORTED_YEAR_START,
                        "YEAR": year,
                    }
                )
        else:
            context.update(
                {
                    "COMMAND_TEXT": command_text,
                    "MODE": "INVALID",
                }
            )

        return {
            **super().get_context(command),
            **context,
        }
