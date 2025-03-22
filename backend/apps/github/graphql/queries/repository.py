"""OWASP repository GraphQL queries."""

import graphene
from django.db import models

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.models.repository import Repository


class RepositoryQuery(BaseQuery):
    """Repository queries."""

    repository = graphene.Field(
        RepositoryNode,
        repository_key=graphene.String(required=True),
    )

    top_contributed_repositories = graphene.List(
        RepositoryNode, login=graphene.String(required=True)
    )

    def resolve_repository(root, info, repository_key):
        """Resolve project."""
        try:
            return Repository.objects.get(key=repository_key)
        except Repository.DoesNotExist:
            return None

    def resolve_top_contributed_repositories(root, info, login):
        """Resolve top repositories for a specific user based on contribution count."""
        return (
            Repository.objects.filter(repositorycontributor__user__login=login)
            .annotate(contributions_count=models.F("repositorycontributor__contributions_count"))
            .order_by("-contributions_count")
        )
