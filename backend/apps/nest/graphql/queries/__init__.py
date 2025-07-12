import strawberry

from apps.nest.graphql.queries.api_key import APIKeyQueries


@strawberry.type
class NestQuery(APIKeyQueries):
    """Nest query."""
