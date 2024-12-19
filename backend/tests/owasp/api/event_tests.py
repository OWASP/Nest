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
                "created_at": "2024-11-01T00:00:00Z",
                "updated_at": "2024-07-02T00:00:00Z",
            },
            True,
        ),
        (
            {
                "name": "biggest event",
                "description": "this is a biggest event",
                "url": "https://github.com/owasp",
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-09-02T00:00:00Z",
            },
            True,
        ),
    ],
)
def test_event_serializer_validation(data, expected):
    serializer = EventSerializer(data=data)
    is_valid = serializer.is_valid()

    assert is_valid == expected
