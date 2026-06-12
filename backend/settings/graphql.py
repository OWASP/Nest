"""GraphQL schema."""

from collections.abc import Callable

import strawberry
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from strawberry.django.views import AsyncGraphQLView
from strawberry.extensions import DisableIntrospection, QueryDepthLimiter, SchemaExtension
from strawberry_django.optimizer import DjangoOptimizerExtension

from apps.api.internal.mutations import ApiMutations
from apps.api.internal.queries import ApiKeyQueries
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
from settings.graphql_context import NestGraphQLContext


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


class NestGraphQLView(AsyncGraphQLView[NestGraphQLContext, None]):
    """Nest GraphQL view."""

    async def get_context(
        self, request: HttpRequest, response: HttpResponse
    ) -> NestGraphQLContext:
        """Return a NestGraphQLContext instance."""
        return NestGraphQLContext(request=request, response=response)


class NestQueryDepthLimiter(QueryDepthLimiter):
    """Query depth limiter configured for the Nest schema."""

    def __init__(self) -> None:
        """Initialize with the Nest schema max query depth."""
        super().__init__(max_depth=5)


extensions: list[type[SchemaExtension] | Callable[[], SchemaExtension]] = [
    NestQueryDepthLimiter,
    DjangoOptimizerExtension,
]

if not settings.DEBUG and not settings.IS_FUZZ_ENVIRONMENT:
    extensions.append(DisableIntrospection)

schema = strawberry.Schema(extensions=extensions, mutation=Mutation, query=Query)
