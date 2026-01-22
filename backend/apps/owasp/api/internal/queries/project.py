"""OWASP project GraphQL queries."""

import strawberry
import strawberry_django
from django.db.models import Q

from apps.github.models.user import User as GithubUser
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.project import Project

MAX_RECENT_PROJECTS_LIMIT = 100
MAX_SEARCH_QUERY_LENGTH = 100
MIN_SEARCH_QUERY_LENGTH = 3
SEARCH_PROJECTS_LIMIT = 100
MAX_PROJECT_KEY_LENGTH = 50


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
        normalized_key = key.strip()

        if not normalized_key or len(normalized_key) > MAX_PROJECT_KEY_LENGTH:
            return None

        try:
            return Project.objects.only("id", "key", "name", "is_active", "created_at").get(
                key=f"www-project-{normalized_key}"
            )
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
        if limit <= 0:
            return []

        limit = min(limit, MAX_RECENT_PROJECTS_LIMIT)

        return list(
            Project.objects.filter(is_active=True)
            .only("id", "key", "name", "created_at", "is_active")
            .order_by("-created_at")[:limit]
        )

    @strawberry_django.field
    def search_projects(self, query: str) -> list[ProjectNode]:
        """Search active projects by name (case-insensitive, partial match)."""
        cleaned_query = query.strip()
        if (
            len(cleaned_query) < MIN_SEARCH_QUERY_LENGTH
            or len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH
        ):
            return []

        return list(
            Project.objects.filter(
                is_active=True,
                name__icontains=cleaned_query,
            )
            .only("id", "key", "name", "is_active")
            .order_by("name")[:SEARCH_PROJECTS_LIMIT]
        )

    @strawberry_django.field
    def is_project_leader(self, info: strawberry.Info, login: str) -> bool:
        """Check if a GitHub login or name is listed as a project leader."""
        if not login or not login.strip():
            return False

        try:
            github_user = GithubUser.objects.get(login=login)
        except GithubUser.DoesNotExist:
            return False

        return Project.objects.filter(
            Q(leaders_raw__icontains=github_user.login)
            | Q(leaders_raw__icontains=(github_user.name or ""))
        ).exists()
