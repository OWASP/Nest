"""GraphQL schema."""

import strawberry

from apps.api.internal.mutations import ApiMutations
from apps.api.internal.queries import ApiKeyQueries
from apps.common.extensions import CacheExtension
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
from apps.owasp.api.internal.queries import OwaspQuery


@strawberry.type
class Mutation(
    ApiMutations,
    ModuleMutation,
    NestMutations,
    ProgramMutation,
):
    """Schema mutations."""


@strawberry.type
class Query(
    ApiKeyQueries,
    GithubQuery,
    MentorshipQuery,
    ModuleQuery,
    OwaspQuery,
    ProgramQuery,
):
    """Schema queries."""


schema = strawberry.Schema(mutation=Mutation, query=Query, extensions=[CacheExtension])
