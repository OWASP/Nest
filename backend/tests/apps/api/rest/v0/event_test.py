from datetime import datetime

import pytest
from django.utils import timezone

from apps.api.rest.v0.event import EventDetail
from apps.owasp.models.event import Event as EventModel

current_timezone = timezone.get_current_timezone()


@pytest.mark.parametrize(
    "event_object",
    [
        EventModel(
            description="this is a sample event",
            end_date=datetime(2023, 6, 15, tzinfo=current_timezone).date(),
            key="sample-event",
            latitude=59.9139,
            longitude=10.7522,
            name="sample event",
            start_date=datetime(2023, 6, 14, tzinfo=current_timezone).date(),
            url="https://github.com/owasp/Nest",
        ),
        EventModel(
            description=None,
            end_date=None,
            key="event-without-end-date",
            latitude=None,
            longitude=None,
            name="event without end date",
            start_date=datetime(2023, 7, 1, tzinfo=current_timezone).date(),
            url=None,
        ),
    ],
)
def test_event_serializer_validation(event_object: EventModel):
    event = EventDetail.from_orm(event_object)

    assert event.description == event_object.description
    end_date = event_object.end_date.isoformat() if event_object.end_date else None
    assert event.end_date == end_date
    assert event.key == event_object.key
    assert event.latitude == event_object.latitude
    assert event.longitude == event_object.longitude
    assert event.name == event_object.name
    assert event.start_date == event_object.start_date.isoformat()
    assert event.url == event_object.url
