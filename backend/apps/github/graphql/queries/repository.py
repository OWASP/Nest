import graphene 

from apps.github.graphql.nodes.repository import RepositoryNode
from apps.common.graphql.queries import BaseQuery
from apps.github.models.repository import Repository


class RepositoryQuery(BaseQuery):
    """Repository Query"""
    repository = graphene.Field(RepositoryNode, key=graphene.String(required=True))

    def resolve_repository(root, info, key):
        """Resolve repository by key."""
        try:
            return Repository.objects.get(key=key)
        except Repository.DoesNotExist:
            return None