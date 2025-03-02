"""OWASP event GraphQL queries."""

from datetime import timezone

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.event import EventNode
from apps.owasp.models.event import Event


class EventQuery(BaseQuery):
    """Event queries."""

    events = graphene.List(EventNode)

    def resolve_events(root, info):
        """Resolve all events."""
        today = timezone.now()

        base_query = Event.objects.filter(start_date__gte=today)

        return base_query.order_by("start_date")
