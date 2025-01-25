"""Nest GraphQL schema."""

import graphene

from apps.owasp.graphql.queries import OwaspQuery


class Query(OwaspQuery):
    """Schema queries."""


schema = graphene.Schema(query=Query)
