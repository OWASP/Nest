"""OWASP event GraphQL node."""

from apps.common.graphql.nodes import BaseNode
from apps.owasp.models.event import Event


class EventNode(BaseNode):
    """Event node."""

    class Meta:
        model = Event
        fields = (
            "name",
            "start_date",
        )
