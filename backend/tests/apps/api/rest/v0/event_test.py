from datetime import datetime

import pytest

from apps.api.rest.v0.event import EventDetail


@pytest.mark.parametrize(
    "event_data",
    [
        {
            "key": "test-event",
            "name": "Test Event",
            "description": "A test event",
            "url": "https://github.com/owasp/Nest",
            "end_date": "2025-03-14T00:00:00",
            "start_date": "2025-03-14T00:00:00",
        },
        {
            "key": "biggest-event",
            "name": "biggest event",
            "description": "this is a biggest event",
            "url": "https://github.com/owasp",
            "end_date": "2023-05-18T00:00:00",
            "start_date": "2022-05-19T00:00:00",
        },
    ],
)
def test_event_serializer_validation(event_data):
    # Create a mock object with nest_key property
    class MockEvent:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    event = EventDetail.from_orm(MockEvent(event_data))

    assert event.description == event_data["description"]
    assert event.end_date == datetime.fromisoformat(event_data["end_date"])
    assert event.key == event_data["key"]
    assert event.name == event_data["name"]
    assert event.start_date == datetime.fromisoformat(event_data["start_date"])
    assert event.url == event_data["url"]
