"""OWASP project GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.owasp.models.project import Project


class RepositoryQuery(BaseQuery):
    """Repository queries."""

    repository = graphene.Field(
        RepositoryNode,
        project_key=graphene.String(required=True),
        repository_key=graphene.String(required=True),
    )

    def resolve_repository(root, info, project_key, repository_key):
        """Resolve project."""
        try:
            return (
                Project.objects.get(key=project_key)
                .repositories.filter(key=repository_key)
                .first()
            )
        except Project.DoesNotExist:
            return None
