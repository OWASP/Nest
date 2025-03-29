"""OWASP committee GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.committee import CommitteeNode
from apps.owasp.models.committee import Committee


class CommitteeQuery(BaseQuery):
    """Committee queries."""

    committee = graphene.Field(CommitteeNode, key=graphene.String(required=True))

    def resolve_committee(root, info, key):
        """Resolve committee by key.

        Args:
            root: The root object.
            info: GraphQL execution info.
            key (str): The key of the committee.

        Returns:
            Committee: The committee object if found, otherwise None.
        """
        try:
            return Committee.objects.get(key=f"www-committee-{key}")
        except Committee.DoesNotExist:
            return None
