"""OWASP project GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.project import ProjectNode
from apps.owasp.models.project import Project


class ProjectQuery(BaseQuery):
    """Project queries."""

    project = graphene.Field(
        ProjectNode,
        key=graphene.String(required=True),
    )

    recent_projects = graphene.List(
        ProjectNode,
        limit=graphene.Int(default_value=8),
    )

    def resolve_project(root, info, key):
        """Resolve project.

        Args:
        ----
            root: The root object.
            info: GraphQL execution info.
            key (str): The key of the project.

        Returns:
        -------
            Project: The project object if found, otherwise None.

        """
        try:
            return Project.objects.get(key=f"www-project-{key}")
        except Project.DoesNotExist:
            return None

    def resolve_recent_projects(root, info, limit):
        """Resolve recent projects.

        Args:
        ----
            root: The root object.
            info: GraphQL execution info.
            limit (int): The maximum number of recent projects to return.

        Returns:
        -------
            QuerySet: A queryset of recent active projects.

        """
        return Project.objects.filter(is_active=True).order_by("-created_at")[:limit]
