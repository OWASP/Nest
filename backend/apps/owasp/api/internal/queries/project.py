"""OWASP project GraphQL queries."""

import strawberry
from django.db.models import Q

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.project import Project


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
        return Project.objects.filter(is_active=True).order_by("-created_at")[:limit]

    @strawberry.field
    def search_projects(self, query: str) -> list[ProjectNode]:
        """Search active projects by name (case-insensitive, partial match)."""
        if not query.strip():
            return []

        return Project.objects.filter(is_active=True, name__icontains=query.strip()).order_by(
            "name"
        )[:3]

    @strawberry.field(permission_classes=[IsAuthenticated])
    def is_project_leader(self, info: strawberry.Info) -> bool:
        """Check if current user is a project leader based on GitHub login or name."""
        user = info.context.request.user

        IsAuthenticated.require_github_user(user)

        github_user = user.github_user

        return Project.objects.filter(
            Q(leaders_raw__icontains=github_user.login)
            | Q(leaders_raw__icontains=(github_user.name or ""))
        ).exists()
