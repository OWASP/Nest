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


@router.get(
    "/",
    summary="Get all events",
    tags=["Events"],
    response={200: list[EventSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_events(
    request: HttpRequest,
    ordering: str | None = Query(None),
) -> list[EventSchema]:
    """
    Retrieves a paginated list of all events, optionally ordered by start or end date.
    
    Parameters:
        ordering (str, optional): Field to order events by. Must be "start_date" or "end_date" to take effect.
    
    Returns:
        list[EventSchema]: A list of serialized event objects.
    """
    events = Event.objects.all()

    if ordering and ordering in VALID_EVENT_ORDERING_FIELDS:
        events = events.order_by(ordering)

    return events
