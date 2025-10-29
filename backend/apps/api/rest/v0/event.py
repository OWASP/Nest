"""Event API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.owasp.models.event import Event as EventModel

router = RouterPaginated(tags=["Events"])


class EventBase(Schema):
    """Base schema for Event (used in list endpoints)."""

    end_date: datetime | None = None
    key: str
    name: str
    start_date: datetime
    url: str | None = None


class Event(EventBase):
    """Schema for Event (minimal fields for list display)."""


class EventDetail(EventBase):
    """Detail schema for Event (used in single item endpoints)."""

    description: str | None = None


class EventError(Schema):
    """Event error schema."""

    message: str


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP events.",
    operation_id="list_events",
    summary="List events",
    response=list[Event],
)
@decorate_view(cache_response())
def list_events(
    request: HttpRequest,
    ordering: Literal["start_date", "-start_date", "end_date", "-end_date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Event]:
    """Get all events."""
    return EventModel.objects.order_by(ordering or "-start_date", "-end_date")


@router.get(
    "/{str:event_id}",
    description="Retrieve an event details.",
    operation_id="get_event",
    response={
        HTTPStatus.NOT_FOUND: EventError,
        HTTPStatus.OK: EventDetail,
    },
    summary="Get event",
)
@decorate_view(cache_response())
def get_event(
    request: HttpRequest,
    event_id: str = Path(..., example="owasp-global-appsec-usa-2025-washington-dc"),
) -> EventDetail | EventError:
    """Get event."""
    if event := EventModel.objects.filter(key__iexact=event_id).first():
        return event

    return Response({"message": "Event not found"}, status=HTTPStatus.NOT_FOUND)
