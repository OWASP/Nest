"""Slack bot gsoc command."""

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_START
from apps.slack.common.gsoc import get_gsoc_year
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
)

SUPPORTED_YEAR_START = 2012
SUPPORTED_ANNOUNCEMENT_YEARS_EXCLUDED = {2012, 2013, 2014, 2015, 2016, 2018}


class Gsoc(CommandBase):
    """Slack bot /gsoc command."""

    @property
    def supported_year_end(self):
        """Upper bound of GSoC years accepted by `/gsoc <year>` (current program year)."""
        return get_gsoc_year()

    @property
    def supported_years(self):
        """Set of GSoC years accepted by `/gsoc <year>`."""
        return set(range(SUPPORTED_YEAR_START, self.supported_year_end + 1))

    @property
    def supported_announcement_years(self):
        """Years for which announcement content is shown."""
        return self.supported_years - SUPPORTED_ANNOUNCEMENT_YEARS_EXCLUDED

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        from apps.owasp.utils.gsoc import get_gsoc_projects

        supported_year_end = self.supported_year_end
        supported_years = self.supported_years
        gsoc_year = supported_year_end
        command_text = command["text"].strip()
        context = {}

        if not command_text or command_text in COMMAND_START:
            context.update(
                {
                    "CONTRIBUTE_CHANNEL_ID": OWASP_CONTRIBUTE_CHANNEL_ID,
                    "GSOC_CHANNEL_ID": OWASP_GSOC_CHANNEL_ID,
                    "MODE": "GENERAL",
                    "GSOC_YEAR": gsoc_year,
                    "PROJECTS_URL": get_absolute_url("/projects"),
                }
            )
        elif command_text.isnumeric():
            year = int(command_text)
            if year in supported_years:
                context.update(
                    {
                        "HAS_ANNOUNCEMENT": year in self.supported_announcement_years,
                        "MODE": "YEAR",
                        "PROJECTS": sorted(get_gsoc_projects(year), key=lambda p: p["name"]),
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
