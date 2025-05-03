"""OWASP repository GraphQL queries."""

from __future__ import annotations

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.models.repository import Repository


class RepositoryQuery(BaseQuery):
    """Repository queries."""

    repository = graphene.Field(
        RepositoryNode,
        organization_key=graphene.String(required=True),
        repository_key=graphene.String(required=True),
    )

    repositories = graphene.List(
        RepositoryNode,
        limit=graphene.Int(default_value=12),
        organization=graphene.String(required=True),
    )

    def resolve_repository(
        root,
        info,
        organization_key: str,
        repository_key: str,
    ) -> Repository | None:
        """Resolve repository by key.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            organization_key (str): The login of the organization.
            repository_key (str): The unique key of the repository.

        Returns:
            Repository or None: The repository object if found, otherwise None.

        """
        try:
            return Repository.objects.select_related("organization").get(
                key__iexact=repository_key,
                organization__login__iexact=organization_key,
            )
        except Repository.DoesNotExist:
            return None

    def resolve_repositories(
        root,
        info,
        organization: str,
        *,
        limit: int = 12,
    ) -> list[Repository]:
        """Resolve repositories.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of repositories to return.
            organization (str): The login of the organization.

        Returns:
            QuerySet: Queryset containing the repositories for the organization.

        """
        return (
            Repository.objects.select_related(
                "organization",
            )
            .filter(
                organization__login__iexact=organization,
            )
            .order_by("-stars_count")[:limit]
        )
