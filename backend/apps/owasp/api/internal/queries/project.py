"""OWASP project GraphQL queries."""

import strawberry
from django.db.models import Q

from apps.github.models.user import User as GithubUser
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.project import Project

MAX_LIMIT = 1000


@strawberry.type
class ProjectQuery:
    """Project queries."""

    @strawberry.field
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

    @strawberry.field
    def recent_projects(self, limit: int = 8) -> list[ProjectNode]:
        """Resolve recent projects.

        Args:
            limit (int): The maximum number of recent projects to return.

        Returns:
            list[ProjectNode]: A list of recent active projects.

        """
        limit = min(limit, MAX_LIMIT)
        return (
            Project.objects.filter(is_active=True).order_by("-created_at")[:limit]
            if limit > 0
            else []
        )

    @strawberry.field
    def search_projects(self, query: str) -> list[ProjectNode]:
        """Search active projects by name (case-insensitive, partial match)."""
        if not query.strip():
            return []

        return Project.objects.filter(
            is_active=True,
            name__icontains=query.strip(),
        ).order_by("name")[:3]

    @strawberry.field
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
