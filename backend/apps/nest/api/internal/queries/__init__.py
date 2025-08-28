import strawberry

from apps.nest.api.internal.queries.api_key import ApiKeyQueries
from apps.nest.api.internal.queries.badge import BadgeQueries


@strawberry.type
class NestQuery(ApiKeyQueries, BadgeQueries):
    """Nest query."""
