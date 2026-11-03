"""OWASP sponsors GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.sponsor import SponsorNode
from apps.owasp.models.sponsor import Sponsor


@strawberry.type
class SponsorQuery:
    """Sponsor queries."""

    @strawberry_django.field
    def sponsors(self) -> list[SponsorNode]:
        """Resolve sponsors."""
        return sorted(
            Sponsor.objects.all(),
            key=lambda x: {
                Sponsor.SponsorType.DIAMOND: 1,
                Sponsor.SponsorType.PLATINUM: 2,
                Sponsor.SponsorType.GOLD: 3,
                Sponsor.SponsorType.SILVER: 4,
                Sponsor.SponsorType.SUPPORTER: 5,
                Sponsor.SponsorType.NOT_SPONSOR: 6,
            }[x.sponsor_type],
        )
