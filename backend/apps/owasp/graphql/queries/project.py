"""Defines the GraphQL queries for OWASP projects."""

import graphene

from apps.owasp.graphql.types.project import ProjectType
from apps.owasp.models.project import Project


class ProjectQueries(graphene.ObjectType):
    """GraphQL queries for OWASP projects."""

    project = graphene.Field(ProjectType, project_id=graphene.ID(), key=graphene.String())

    def resolve_project(self, info, project_id=None, key=None):
        """Resolve a project by its ID or key."""
        if id:
            return Project.objects.get(id=id)
        if key:
            return Project.objects.get(key=key)
        return None
