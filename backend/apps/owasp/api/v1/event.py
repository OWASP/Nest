"""Event API."""

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.event import Event

router = Router()


class EventSchema(Schema):
    """Schema for Event."""

    description: str
    name: str
    url: str


@router.get("/", response=list[EventSchema])
@paginate(PageNumberPagination, page_size=100)
def list_events(request: HttpRequest) -> list[EventSchema]:
    """Get all events."""
    events = Event.objects.all()
    if not events:
        raise HttpError(404, "Events not found")
    return events
