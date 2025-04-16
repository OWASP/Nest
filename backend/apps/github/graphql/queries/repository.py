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
        organization_key=graphene.String(required=True),
    )

    repositories = graphene.List(
        RepositoryNode,
        organization=graphene.String(required=True),
        limit=graphene.Int(default_value=12),
    )

    def resolve_repository(root, info, organization_key, repository_key):
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

    def resolve_repositories(root, info, organization, limit):
        """Resolve repositories.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            organization (str): The login of the organization.
            limit (int): Maximum number of repositories to return.

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
