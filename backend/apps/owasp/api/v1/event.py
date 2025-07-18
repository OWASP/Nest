"""Event API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.event import Event

router = Router()


class EventSchema(Schema):
    """Schema for Event."""

    description: str
    name: str
    end_date: datetime
    start_date: datetime
    url: str


VALID_EVENT_ORDERING_FIELDS = {"start_date", "end_date"}


@router.get("/", response={200: list[EventSchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_events(
    request: HttpRequest,
    ordering: str | None = Query(None),
) -> list[EventSchema]:
    """Get all events."""
    events = Event.objects.all()

    if ordering and ordering in VALID_EVENT_ORDERING_FIELDS:
        events = events.order_by(ordering)

    return events
