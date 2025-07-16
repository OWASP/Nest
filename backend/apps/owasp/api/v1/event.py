"""Event API."""

from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import PAGE_SIZE
from apps.owasp.models.event import Event

router = Router()


class EventFilterSchema(FilterSchema):
    """Filter schema for Event."""

    name: str | None = None


class EventSchema(Schema):
    """Schema for Event."""

    description: str
    name: str
    url: str


@router.get("/", response={200: list[EventSchema], 404: dict})
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_events(
    request: HttpRequest, filters: EventFilterSchema = Query(...)
) -> list[EventSchema] | dict:
    """Get all events."""
    events = filters.filter(Event.objects.all())
    if not events.exists():
        raise HttpError(404, "Events not found")
    return events
