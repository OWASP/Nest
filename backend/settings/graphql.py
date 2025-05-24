"""GraphQL schema."""

import graphene

from apps.github.graphql.queries import GithubQuery
from apps.nest.graphql.mutations.user import AuthUserMutation
from apps.owasp.graphql.queries import OwaspQuery


class Query(GithubQuery, OwaspQuery):
    """Schema queries."""


class Mutation(AuthUserMutation):
    """Schema mutations."""


schema = graphene.Schema(query=Query, mutation=Mutation)
