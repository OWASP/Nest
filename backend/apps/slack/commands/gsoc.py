"""Slack bot gsoc command."""

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_START
from apps.slack.common.gsoc import get_gsoc_year
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
)
from apps.slack.utils import get_gsoc_projects

SUPPORTED_YEAR_START = 2012
SUPPORTED_ANNOUNCEMENT_YEARS_EXCLUDED = {2012, 2013, 2014, 2015, 2016, 2018}


def get_supported_year_end():
    """Get the current supported year end based on the current date."""
    return get_gsoc_year()


def get_supported_years():
    """Get the set of supported GSoC years."""
    return set(range(SUPPORTED_YEAR_START, get_supported_year_end() + 1))


def get_supported_announcement_years():
    """Get the set of years with announcements."""
    return get_supported_years() - SUPPORTED_ANNOUNCEMENT_YEARS_EXCLUDED


class Gsoc(CommandBase):
    """Slack bot /gsoc command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        gsoc_year = get_gsoc_year()
        supported_years = get_supported_years()
        supported_year_end = get_supported_year_end()
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
            if year in supported_years:
                context.update(
                    {
                        "HAS_ANNOUNCEMENT": year in get_supported_announcement_years(),
                        "MODE": "YEAR",
                        "PROJECTS": sorted(get_gsoc_projects(year), key=lambda p: p["idx_name"]),
                        "YEAR": year,
                    }
                )
            else:
                context.update(
                    {
                        "MODE": "UNSUPPORTED_YEAR",
                        "SUPPORTED_YEAR_END": supported_year_end,
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
