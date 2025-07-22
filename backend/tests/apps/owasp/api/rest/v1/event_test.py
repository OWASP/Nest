from datetime import datetime

import pytest

from apps.owasp.api.rest.v1.event import EventSchema


@pytest.mark.parametrize(
    "event_data",
    [
        {
            "name": "Test Event",
            "description": "A test event",
            "url": "https://github.com/owasp/Nest",
            "end_date": "2025-03-14T00:00:00",
            "start_date": "2025-03-14T00:00:00",
        },
        {
            "name": "biggest event",
            "description": "this is a biggest event",
            "url": "https://github.com/owasp",
            "end_date": "2023-05-18T00:00:00",
            "start_date": "2022-05-19T00:00:00",
        },
    ],
)
def test_event_serializer_validation(event_data):
    event = EventSchema(**event_data)
    assert event.name == event_data["name"]
    assert event.description == event_data["description"]
    assert event.url == event_data["url"]
    assert event.end_date == datetime.fromisoformat(event_data["end_date"])
    assert event.start_date == datetime.fromisoformat(event_data["start_date"])
