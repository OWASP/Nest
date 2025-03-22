"""OWASP repository GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.models.repository import Repository


class RepositoryQuery(BaseQuery):
    """Repository queries."""

    repository = graphene.Field(
        RepositoryNode,
        repository_key=graphene.String(required=True),
    )

    def resolve_repository(root, info, repository_key):
        """Resolve project."""
        try:
            return Repository.objects.get(key=repository_key)
        except Repository.DoesNotExist:
            return None
