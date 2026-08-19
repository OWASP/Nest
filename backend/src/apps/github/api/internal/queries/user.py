"""OWASP user GraphQL queries."""

import strawberry
import strawberry_django
from django.db.models import Q, Sum

from apps.common.constants import (
    MAX_SEARCH_QUERY_LENGTH,
    MIN_SEARCH_QUERY_LENGTH,
    SEARCH_LIMIT,
)
from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.api.internal.nodes.user import USER_BADGES_PREFETCH, UserNode
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.nest.api.internal.permissions import IsAuthenticated

MAX_LIMIT = 1000


@strawberry.type
class UserQuery:
    """User queries."""

    @strawberry_django.field
    def top_contributed_repositories(
        self,
        login: str,
    ) -> list[RepositoryNode]:
        """Resolve user top repositories.

        Args:
            login (str): The login of the user.

        Returns:
            list: List of repositories the user has contributed to.

        """
        return [
            rc.repository
            for rc in RepositoryContributor.objects.select_related(
                "repository",
                "repository__organization",
            )
            .filter(user__login=login)
            .order_by("-contributions_count")
        ]

    @strawberry_django.field
    def user(
        self,
        login: str,
    ) -> UserNode | None:
        """Resolve user by login.

        Args:
            login (str): The login of the user.

        Returns:
            User or None: The user object if found, otherwise None.

        """
        return (
            User.objects.filter(has_public_member_page=True, login=login)
            .prefetch_related(USER_BADGES_PREFETCH)
            .first()
        )

    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def search_users(self, query: str) -> list[UserNode]:
        """Search GitHub users by login or name."""
        cleaned_query = query.strip()
        if (
            len(cleaned_query) < MIN_SEARCH_QUERY_LENGTH
            or len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH
        ):
            return []

        return list(
            User.objects.filter(
                Q(has_public_member_page=True),
                Q(login__icontains=cleaned_query) | Q(name__icontains=cleaned_query),
            ).order_by("login")[:SEARCH_LIMIT]
        )

    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def entity_contributors(
        self,
        project_key: str | None = None,
        chapter_key: str | None = None,
        limit: int = 15,
    ) -> list[UserNode]:
        """Fetch top contributors for a project or chapter in a single JOIN query."""
        if not project_key and not chapter_key:
            return []

        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        if project_key:
            clean_project_key = project_key.strip().removeprefix("www-project-")
            filter_q = Q(
                repositorycontributor__repository__project_set__key__iexact=(
                    f"www-project-{clean_project_key}"
                )
            )
        elif chapter_key:
            clean_chapter_key = chapter_key.strip().removeprefix("www-chapter-")
            filter_q = Q(
                repositorycontributor__repository__key__iexact=(f"www-chapter-{clean_chapter_key}")
            )
        else:
            return []

        return list(
            User.objects.filter(filter_q)
            .annotate(total_contributions=Sum("repositorycontributor__contributions_count"))
            .prefetch_related(USER_BADGES_PREFETCH)
            .order_by("-total_contributions")[:normalized_limit]
        )
