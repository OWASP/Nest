"""GraphQL schema."""

import strawberry

from apps.github.graphql.queries import GithubQuery
from apps.nest.graphql.mutations.user import UserMutations
from apps.owasp.graphql.queries import OwaspQuery


@strawberry.type
class Query(GithubQuery, OwaspQuery):
    """Schema queries."""


class Mutation(UserMutations):
    """Schema mutations."""


schema = strawberry.Schema(query=Query, mutation=Mutation)
