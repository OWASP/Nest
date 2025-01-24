import graphene

from apps.common.schema import BaseQuery
from apps.owasp.graphql.queries import OWASPQuery


class Query(BaseQuery, OWASPQuery):
    pass


schema = graphene.Schema(query=Query)
