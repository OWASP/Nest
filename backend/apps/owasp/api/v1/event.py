"""Event API."""

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.owasp.models.event import Event

router = RouterPaginated()


class EventSchema(Schema):
    """Schema for Event."""

    description: str
    name: str
    url: str


@router.get("/", response=list[EventSchema])
def list_events(request: HttpRequest) -> list[EventSchema] | HttpError:
    """Get all events."""
    events = Event.objects.all()
    if not events:
        raise HttpError(404, "Events not found")
    return events
