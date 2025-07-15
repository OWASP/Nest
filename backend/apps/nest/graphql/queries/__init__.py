import strawberry

from apps.nest.graphql.queries.api_key import ApiKeyQueries


@strawberry.type
class NestQuery(ApiKeyQueries):
    """Nest query."""
