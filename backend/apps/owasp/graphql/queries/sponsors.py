"""OWASP sponsors GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.sponsors import SponsorNode
from apps.owasp.models.sponsors import Sponsor


class SponsorQuery(BaseQuery):
    """Sponsor queries."""

    sponsors = graphene.List(SponsorNode)

    def resolve_sponsors(root, info):
        """Resolve sponsors."""
        return Sponsor.objects.all()
