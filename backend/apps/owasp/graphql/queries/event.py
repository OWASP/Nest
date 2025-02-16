"""OWASP event GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.event import EventNode
from apps.owasp.models.event import Event


class EventQuery(BaseQuery):
    """Event queries."""

    events = graphene.List(EventNode)

    def resolve_events(root, info):
        """Resolve all events."""
        return Event.objects.all()
