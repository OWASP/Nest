"""OWASP sponsors GraphQL queries."""

import graphene
from django.db.models import Case, IntegerField, Value, When

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.sponsor import SponsorNode
from apps.owasp.models.sponsor import Sponsor


class SponsorQuery(BaseQuery):
    """Sponsor queries."""

    sponsors = graphene.List(SponsorNode)

    def resolve_sponsors(root, info):
        """Resolve sponsors."""
        priority_order = Case(
            *[
                When(sponsor_type=s_type, then=Value(index))
                for index, s_type in enumerate(Sponsor.SponsorType)
            ],
            output_field=IntegerField(),
        )
        return Sponsor.objects.annotate(
            priority_order=priority_order,
        ).order_by("priority_order")
