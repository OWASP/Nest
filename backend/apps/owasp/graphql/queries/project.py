import graphene

from apps.owasp.graphql.types.project import ProjectType
from apps.owasp.models.project import Project


class ProjectQueries(graphene.ObjectType):
    project = graphene.Field(ProjectType, id=graphene.ID(), key=graphene.String())

    def resolve_project(self, info, id=None, key=None):
        if id:
            return Project.objects.get(id=id)
        if key:
            return Project.objects.get(key=key)
        return None
