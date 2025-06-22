import pytest

from apps.owasp.api.event import EventSchema


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "name": "Test Event",
                "description": "A test event",
                "url": "https://github.com/owasp/Nest",
            },
            True,
        ),
        (
            {
                "name": "biggest event",
                "description": "this is a biggest event",
                "url": "https://github.com/owasp",
            },
            True,
        ),
    ],
)
def test_event_serializer_validation(data, expected):
    event = EventSchema(**data)
    assert event.name == data["name"]
    assert event.description == data["description"]
    assert event.url == data["url"]
