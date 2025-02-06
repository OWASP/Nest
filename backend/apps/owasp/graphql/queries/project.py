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
        repo_key=graphene.String(required=False),  # Optional
    )

    def resolve_project(root, info, key, repo_key=None):
        """Resolve project by key, optionally filtering repositories by repo_key."""
        try:
            return Project.objects.get(key=key)
        except Project.DoesNotExist:
            return None
