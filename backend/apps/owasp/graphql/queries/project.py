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

    def resolve_project(root, info, key):
        """Resolve project."""
        try:
            return Project.objects.get(key=key)
        except Project.DoesNotExist:
            return None
