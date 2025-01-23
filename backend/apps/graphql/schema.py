import graphene
from apps.owasp.models.project import Project
from apps.graphql.types.project import ProjectType

class Query(graphene.ObjectType):
    project = graphene.Field(ProjectType, key=graphene.String(required=True))

    def resolve_project(self, info, key):
        return Project.objects.get(key=key)

schema = graphene.Schema(query=Query)