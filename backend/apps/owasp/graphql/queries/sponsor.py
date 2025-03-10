"""OWASP sponsors GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.sponsor import SponsorNode
from apps.owasp.models.sponsor import Sponsor


class SponsorQuery(BaseQuery):
    """Sponsor queries."""

    sponsors = graphene.List(SponsorNode)

    def resolve_sponsors(root, info):
        """Resolve sponsors."""
        priority_order = {
            Sponsor.SponsorType.DIAMOND: 1,
            Sponsor.SponsorType.PLATINUM: 2,
            Sponsor.SponsorType.GOLD: 3,
            Sponsor.SponsorType.SILVER: 4,
            Sponsor.SponsorType.SUPPORTER: 5,
            Sponsor.SponsorType.NOT_SPONSOR: 6,
        }
        return sorted(Sponsor.objects.all(), key=lambda x: priority_order[x.sponsor_type])
