"""GraphQL schema."""

import strawberry

from apps.github.graphql.queries import GithubQuery
from apps.nest.graphql.mutations.user import UserMutations
from apps.owasp.graphql.queries import OwaspQuery


class Mutation(UserMutations):
    """Schema mutations."""


@strawberry.type
class Query(GithubQuery, OwaspQuery):
    """Schema queries."""


schema = strawberry.Schema(mutation=Mutation, query=Query)
