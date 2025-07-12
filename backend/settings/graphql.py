"""GraphQL schema."""

import strawberry

from apps.github.graphql.queries import GithubQuery
from apps.nest.graphql.mutations import NestMutations
from apps.nest.graphql.queries import NestQuery
from apps.owasp.graphql.queries import OwaspQuery


@strawberry.type
class Mutation(NestMutations):
    """Schema mutations."""


@strawberry.type
class Query(GithubQuery, NestQuery, OwaspQuery):
    """Schema queries."""


schema = strawberry.Schema(mutation=Mutation, query=Query)
