from datetime import datetime

import pytest

from apps.api.rest.v0.event import EventDetail


@pytest.mark.parametrize(
    "event_data",
    [
        {
            "description": "A test event",
            "end_date": "2025-03-14T00:00:00Z",
            "key": "test-event",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "name": "Test Event",
            "start_date": "2025-03-14T00:00:00Z",
            "url": "https://github.com/owasp/Nest",
        },
        {
            "description": "this is a biggest event",
            "end_date": "2023-05-18T00:00:00Z",
            "key": "biggest-event",
            "latitude": 59.9139,
            "longitude": 10.7522,
            "name": "biggest event",
            "start_date": "2022-05-19T00:00:00Z",
            "url": "https://github.com/owasp",
        },
    ],
)
def test_event_serializer_validation(event_data):
    event = EventDetail(**event_data)

    assert event.description == event_data["description"]
    assert event.end_date == datetime.fromisoformat(event_data["end_date"])
    assert event.key == event_data["key"]
    assert event.latitude == event_data["latitude"]
    assert event.longitude == event_data["longitude"]
    assert event.name == event_data["name"]
    assert event.start_date == datetime.fromisoformat(event_data["start_date"])
    assert event.url == event_data["url"]
