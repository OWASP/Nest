"""OWASP event GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.event import EventNode
from apps.owasp.models.event import Event

MAX_LIMIT = 1000


@strawberry.type
class EventQuery:
    """Event queries."""

    @strawberry.field
    def upcoming_events(self, limit: int = 6) -> list[EventNode]:
        """Resolve upcoming events."""
        return Event.upcoming_events()[:limit] if (limit := min(limit, MAX_LIMIT)) > 0 else []
