"""GraphQL schema."""

import strawberry

from apps.github.graphql.queries import GithubQuery
from apps.owasp.graphql.queries import OwaspQuery


@strawberry.type
class Query(GithubQuery, OwaspQuery):
    """Schema queries."""


schema = strawberry.Schema(query=Query)
