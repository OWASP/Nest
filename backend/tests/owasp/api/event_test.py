import pytest

from apps.owasp.api.event import EventSerializer


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
    serializer = EventSerializer(data=data)
    is_valid = serializer.is_valid()

    assert is_valid == expected
