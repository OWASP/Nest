"""GraphQL schema."""

import strawberry

from apps.github.graphql.queries import GithubQuery
from apps.mentorship.graphql.mutations import (
    MentorshipMutations,
    ModuleMutation,
    ProgramMutation,
)
from apps.mentorship.graphql.queries import (
    MentorshipQuery,
    ModuleQuery,
    ProgramQuery,
)
from apps.nest.graphql.mutations import NestMutations
from apps.nest.graphql.queries import NestQuery
from apps.owasp.graphql.queries import OwaspQuery


@strawberry.type
class Mutation(
    MentorshipMutations,
    ModuleMutation,
    ProgramMutation,
    NestMutations,
):
    """Schema mutations."""


@strawberry.type
class Query(
    GithubQuery,
    MentorshipQuery,
    ModuleQuery,
    ProgramQuery,
    NestQuery,
    OwaspQuery,
):
    """Schema queries."""


schema = strawberry.Schema(query=Query, mutation=Mutation)
