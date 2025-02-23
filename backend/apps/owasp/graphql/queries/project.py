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
        """Resolve project."""
        try:
            return Project.objects.get(key=f"www-project-{key}")
        except Project.DoesNotExist:
            return None

    def resolve_recent_projects(root, info, limit):
        """Resolve recent projects."""
        return Project.objects.filter(is_active=True).order_by("-created_at")[:limit]
