"""Defines the GraphQL queries for OWASP projects."""

import graphene

from apps.owasp.graphql.types.project import ProjectType
from apps.owasp.models.project import Project


class ProjectQueries(graphene.ObjectType):
    """GraphQL queries for OWASP projects."""

    project = graphene.Field(ProjectType, key=graphene.String())

    def resolve_project(self, info, key=None):
        """Resolve a project by its key."""
        if key:
            return Project.objects.get(key=key)
        return None
