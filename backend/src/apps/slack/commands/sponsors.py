"""Slack bot sponsors command."""

from django.db.models import Case, IntegerField, Value, When

from apps.common.constants import OWASP_URL
from apps.owasp.models.sponsor import Sponsor
from apps.slack.commands.command import CommandBase

SPONSOR_TIER_ORDER = Case(
    When(sponsor_type=Sponsor.SponsorType.DIAMOND, then=Value(1)),
    When(sponsor_type=Sponsor.SponsorType.PLATINUM, then=Value(2)),
    When(sponsor_type=Sponsor.SponsorType.GOLD, then=Value(3)),
    When(sponsor_type=Sponsor.SponsorType.SILVER, then=Value(4)),
    When(sponsor_type=Sponsor.SponsorType.SUPPORTER, then=Value(5)),
    When(sponsor_type=Sponsor.SponsorType.NOT_SPONSOR, then=Value(6)),
    default=Value(7),
    output_field=IntegerField(),
)


class Sponsors(CommandBase):
    """Slack bot /sponsors command."""

    def get_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "SPONSORS": Sponsor.objects.order_by(SPONSOR_TIER_ORDER, "sort_name")[:10],
            "SPONSORS_PAGE_NAME": "OWASP Supporters",
            "SPONSORS_PAGE_URL": f"{OWASP_URL}/supporters/",
        }
