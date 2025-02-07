"""OWASP committee GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.committee import CommitteeNode
from apps.owasp.models.committee import Committee


class CommitteeQuery(BaseQuery):
    """Committee queries."""

    committee = graphene.Field(CommitteeNode, key=graphene.String(required=True))

    def resolve_committee(root, info, key):
        """Resolve committee by key."""
        try:
            normalized_key = "www-committee-" + key
            return Committee.objects.get(key=normalized_key)
        except Committee.DoesNotExist:
            return None
