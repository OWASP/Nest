"""Event API."""

from datetime import datetime
from typing import Literal

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


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP events.",
    operation_id="list_events",
    summary="List events",
    tags=["Events"],
    response={200: list[EventSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_events(
    request: HttpRequest,
    ordering: Literal["start_date", "-start_date", "end_date", "-end_date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[EventSchema]:
    """Get all events."""
    return Event.objects.order_by(ordering or "-start_date")
