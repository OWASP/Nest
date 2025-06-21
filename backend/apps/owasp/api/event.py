"""Event API."""

from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.owasp.models.event import Event

router = Router()


class EventSchema(BaseModel):
    """Schema for Event."""

    model_config = {"from_attributes": True}

    description: str
    name: str
    url: str


@router.get("/", response=list[EventSchema])
def list_events(request: HttpRequest) -> list[EventSchema]:
    """Get all events."""
    return Event.objects.all()
