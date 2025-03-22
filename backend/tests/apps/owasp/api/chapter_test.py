import pytest

from apps.owasp.api.chapter import ChapterSerializer


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "name": "OWASP Nagoya",
                "description": "A test chapter",
                "level": "other",
                "created_at": "2024-11-01T00:00:00Z",
                "updated_at": "2024-07-02T00:00:00Z",
            },
            True,
        ),
        (
            {
                "name": "OWASP something",
                "description": "it is description",
                "level": "github",
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-09-02T00:00:00Z",
            },
            True,
        ),
    ],
)
def test_chapter_serializer_validation(data, expected):
    serializer = ChapterSerializer(data=data)
    is_valid = serializer.is_valid()

    assert is_valid == expected
