"""OWASP project GraphQL queries."""

import strawberry

from apps.owasp.graphql.nodes.project import ProjectNode
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
