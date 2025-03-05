"""OWASP event GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.event import EventNode
from apps.owasp.models.event import Event


class EventQuery(BaseQuery):
    """Event queries."""

    upcoming_events = graphene.List(EventNode, limit=graphene.Int(default_value=8))

    def resolve_upcoming_events(root, info, limit):
        """Resolve all events."""
        return Event.objects.order_by("start_date")[:limit]
