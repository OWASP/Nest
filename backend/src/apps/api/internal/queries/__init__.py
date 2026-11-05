import strawberry

from apps.api.internal.queries.api_key import ApiKeyQueries


@strawberry.type
class NestQuery(ApiKeyQueries):
    """Nest query."""
