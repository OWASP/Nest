"""GraphQL schema."""

import graphene

from apps.github.graphql.queries import GithubQuery
from apps.owasp.graphql.queries import OwaspQuery


class Query(GithubQuery, OwaspQuery):
    """Schema queries."""


schema = graphene.Schema(query=Query)
