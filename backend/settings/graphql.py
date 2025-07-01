"""GraphQL schema."""

import strawberry

from apps.github.graphql.queries import GithubQuery
from apps.mentorship.graphql.mutations import ProgramMutation
from apps.mentorship.graphql.queries import ProgramQuery
from apps.nest.graphql.mutations import UserMutations
from apps.owasp.graphql.queries import OwaspQuery


@strawberry.type
class Mutation(ProgramMutation, UserMutations):
    """Schema mutations."""


@strawberry.type
class Query(
    GithubQuery,
    ProgramQuery,
    OwaspQuery,
):
    """Schema queries."""


schema = strawberry.Schema(mutation=Mutation, query=Query)
