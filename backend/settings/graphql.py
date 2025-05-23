"""GraphQL schema."""

import graphene

from apps.github.graphql.queries import GithubQuery
from apps.nest.graphql.queries.user import AuthUserQuery
from apps.owasp.graphql.queries import OwaspQuery


class Query(GithubQuery, OwaspQuery):
    """Schema queries."""


class Mutation(AuthUserQuery):
    """Schema mutations."""


schema = graphene.Schema(query=Query, mutation=Mutation)
