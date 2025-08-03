"""GraphQL schema."""

import strawberry

from apps.github.api.internal.queries import GithubQuery
from apps.nest.api.internal.mutations import NestMutations
from apps.nest.api.internal.queries import NestQuery
from apps.owasp.api.internal.queries import OwaspQuery


@strawberry.type
class Mutation(NestMutations):
    """Schema mutations."""


@strawberry.type
class Query(GithubQuery, NestQuery, OwaspQuery):
    """Schema queries."""


schema = strawberry.Schema(mutation=Mutation, query=Query)
