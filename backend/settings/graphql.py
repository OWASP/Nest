"""Defines the GraphQL schema for the application."""

import graphene

from apps.common.schema import BaseQuery
from apps.owasp.graphql.queries import OWASPQuery


class Query(BaseQuery, OWASPQuery):
    """Combines base and OWASP queries."""


schema = graphene.Schema(query=Query)
