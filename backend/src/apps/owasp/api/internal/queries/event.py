"""OWASP event GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.owasp.api.internal.nodes.event import EventNode
from apps.owasp.models.event import Event

MAX_LIMIT = 1000


@strawberry.type
class EventQuery:
    """Event queries."""

    @strawberry_django.field
    def upcoming_events(self, limit: int = 6) -> list[EventNode]:
        """Resolve upcoming events."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return Event.upcoming_events()[:normalized_limit]
