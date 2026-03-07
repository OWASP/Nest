"""OWASP project GraphQL queries."""

import strawberry
import strawberry_django
from django.db.models import Q
from strawberry_django.pagination import OffsetPaginationInput

from apps.common.utils import normalize_limit
from apps.github.models.user import User as GithubUser
from apps.owasp.api.internal.filters.project import ProjectFilter
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.api.internal.ordering.project import ProjectOrder
from apps.owasp.models.project import Project

MAX_RECENT_PROJECTS_LIMIT = 1000
MAX_SEARCH_QUERY_LENGTH = 100
MAX_PROJECTS_LIMIT = 1000
MAX_OFFSET = 10000


@strawberry.type
class ProjectQuery:
    """Project queries."""

    @strawberry_django.field
    def project(self, key: str) -> ProjectNode | None:
        """Resolve project.

        Args:
            key (str): The key of the project.

        Returns:
            ProjectNode | None: The project node if found, otherwise None.

        """
        try:
            return Project.objects.get(key=f"www-project-{key}")
        except Project.DoesNotExist:
            return None

    @strawberry_django.field
    def recent_projects(self, limit: int = 8) -> list[ProjectNode]:
        """Resolve recent projects.

        Args:
            limit (int): The maximum number of recent projects to return.

        Returns:
            list[ProjectNode]: A list of recent active projects.

        """
        if (normalized_limit := normalize_limit(limit, MAX_RECENT_PROJECTS_LIMIT)) is None:
            return []

        return Project.objects.filter(is_active=True).order_by("-created_at")[:normalized_limit]

    @strawberry_django.field(
        filters=ProjectFilter,
        ordering=ProjectOrder,
        pagination=True,
    )
    def projects(
        self,
        filters: ProjectFilter | None = None,
        ordering: list[ProjectOrder] | None = None,
        pagination: OffsetPaginationInput | None = None,
    ) -> list[ProjectNode]:
        """Resolve active projects with optional category filter, ordering, and pagination."""
        queryset = Project.objects.filter(is_active=True)

        if not ordering:
            queryset = queryset.order_by("-stars_count", "-created_at")

        if pagination:
            if pagination.offset < 0:
                return []
            pagination.offset = min(pagination.offset, MAX_OFFSET)

            if pagination.limit is not None and pagination.limit is not strawberry.UNSET:
                if pagination.limit <= 0:
                    return []
                pagination.limit = min(pagination.limit, MAX_PROJECTS_LIMIT)

        return queryset

    @strawberry_django.field(
        filters=ProjectFilter,
        ordering=ProjectOrder,
        pagination=True,
    )
    def search_projects(
        self,
        query: str = "",
        filters: ProjectFilter | None = None,
        ordering: list[ProjectOrder] | None = None,
        pagination: OffsetPaginationInput | None = None,
    ) -> list[ProjectNode]:
        """Search active projects by name with optional filters and sorting."""
        cleaned_query = query.strip()

        if len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH:
            return []

        base_queryset = Project.objects.filter(is_active=True)

        if cleaned_query:
            bounded_query = cleaned_query[:MAX_SEARCH_QUERY_LENGTH]
            base_queryset = base_queryset.filter(name__icontains=bounded_query)

        if not ordering:
            base_queryset = base_queryset.order_by("-stars_count", "-created_at")

        if pagination:
            if pagination.offset < 0:
                return []
            pagination.offset = min(pagination.offset, MAX_OFFSET)

            if pagination.limit is not None and pagination.limit is not strawberry.UNSET:
                if pagination.limit <= 0:
                    return []
                pagination.limit = min(pagination.limit, MAX_PROJECTS_LIMIT)

        return base_queryset

    @strawberry.field
    def search_projects_count(
        self,
        query: str = "",
        filters: ProjectFilter | None = None,
    ) -> int:
        """Return total count of matching projects for pagination."""
        cleaned_query = query.strip()

        if len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH:
            return 0

        base_queryset = Project.objects.filter(is_active=True)

        if cleaned_query:
            base_queryset = base_queryset.filter(name__icontains=cleaned_query)

        if filters:
            base_queryset = strawberry_django.filters.apply(filters, base_queryset)

        return base_queryset.count()

    @strawberry_django.field
    def is_project_leader(self, info: strawberry.Info, login: str) -> bool:
        """Check if a GitHub login or name is listed as a project leader."""
        try:
            github_user = GithubUser.objects.get(login=login)
        except GithubUser.DoesNotExist:
            return False

        return Project.objects.filter(
            Q(leaders_raw__icontains=github_user.login)
            | Q(leaders_raw__icontains=(github_user.name or ""))
        ).exists()
