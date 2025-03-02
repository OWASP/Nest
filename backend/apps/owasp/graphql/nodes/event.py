"""OWASP event GraphQL node."""

from apps.common.graphql.nodes import BaseNode
from apps.owasp.models.event import Event


class EventNode(BaseNode):
    """Event node."""

    class Meta:
        model = Event
        fields = (
            "category",
            "end_date",
            "description",
            "key",
            "name",
            "start_date",
            "url",
        )
