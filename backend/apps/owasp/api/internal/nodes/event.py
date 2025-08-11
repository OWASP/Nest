"""OWASP event GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.event import Event


@strawberry_django.type(
    Event,
    fields=[
        "category",
        "description",
        "end_date",
        "key",
        "name",
        "start_date",
        "suggested_location",
        "summary",
        "url",
    ],
)
class EventNode(strawberry.relay.Node):
    """Event node."""
