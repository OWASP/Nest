import pytest

from apps.owasp.api.v1.event import EventSchema


@pytest.mark.parametrize(
    "event_data",
    [
        {
            "name": "Test Event",
            "description": "A test event",
            "url": "https://github.com/owasp/Nest",
        },
        {
            "name": "biggest event",
            "description": "this is a biggest event",
            "url": "https://github.com/owasp",
        },
    ],
)
def test_event_serializer_validation(event_data):
    event = EventSchema(**event_data)
    assert event.name == event_data["name"]
    assert event.description == event_data["description"]
    assert event.url == event_data["url"]
