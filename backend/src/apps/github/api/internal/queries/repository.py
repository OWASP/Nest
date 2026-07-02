"""OWASP repository GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.models.repository import Repository

MAX_LIMIT = 1000


@strawberry.type
class RepositoryQuery:
    """Repository queries."""

    @strawberry_django.field
    def repository(
        self,
        organization_key: str,
        repository_key: str,
    ) -> RepositoryNode | None:
        """Resolve repository by key.

        Args:
            organization_key (str): The login of the organization.
            repository_key (str): The unique key of the repository.

        Returns:
            RepositoryNode | None: The repository node if found, otherwise None.

        """
        try:
            return Repository.objects.select_related("organization").get(
                key__iexact=repository_key,
                organization__login__iexact=organization_key,
            )
        except Repository.DoesNotExist:
            return None

    @strawberry_django.field
    def repositories(
        self,
        organization: str,
        *,
        limit: int = 12,
    ) -> list[RepositoryNode]:
        """Resolve repositories.

        Args:
            organization (str): The login of the organization.
            limit (int): Maximum number of repositories to return.

        Returns:
            list[RepositoryNode]: A list of repositories.

        """
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return Repository.objects.filter(
            organization__login__iexact=organization,
        ).order_by("-stars_count")[:normalized_limit]
