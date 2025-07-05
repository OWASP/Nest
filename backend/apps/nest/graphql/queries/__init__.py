import strawberry

from apps.nest.graphql.queries.apikey import APIKeyQueries


@strawberry.type
class NestQuery(APIKeyQueries):
    """Nest query."""
