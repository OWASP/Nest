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
        """Resolve repository by key.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            repository_key (str): The unique key of the repository.

        Returns:
            Repository or None: The repository object if found, otherwise None.

        """
        try:
            return Repository.objects.get(key=repository_key)
        except Repository.DoesNotExist:
            return None
