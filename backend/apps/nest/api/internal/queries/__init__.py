import strawberry

from apps.nest.api.internal.queries.api_key import ApiKeyQueries
from apps.nest.api.internal.queries.badge import BadgeQueries
from apps.nest.api.internal.queries.user import UserQueries


@strawberry.type
class NestQuery(ApiKeyQueries, BadgeQueries, UserQueries):
    """Nest query."""
