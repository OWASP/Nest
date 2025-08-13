"""GraphQL schema."""

import strawberry

from apps.github.api.internal.queries import GithubQuery
from apps.mentorship.api.internal.mutations import (
    ModuleMutation,
    ProgramMutation,
)
from apps.mentorship.api.internal.queries import (
    MentorshipQuery,
    ModuleQuery,
    ProgramQuery,
)
from apps.nest.api.internal.mutations import NestMutations
from apps.nest.api.internal.queries import NestQuery
from apps.owasp.api.internal.queries import OwaspQuery


@strawberry.type
class Mutation(
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
    NestQuery,
    OwaspQuery,
    ProgramQuery,
):
    """Schema queries."""


schema = strawberry.Schema(mutation=Mutation, query=Query)
