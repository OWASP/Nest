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
            normalized_key = "www-project-" + key
            return Project.objects.get(key=normalized_key)
        except Project.DoesNotExist:
            return None
