import strawberry

from apps.nest.api.internal.queries.api_key import ApiKeyQueries


@strawberry.type
class NestQuery(ApiKeyQueries, BadgeQueries):
    """Nest query."""
