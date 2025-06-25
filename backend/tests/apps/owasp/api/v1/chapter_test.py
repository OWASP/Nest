from datetime import datetime

import pytest

from apps.owasp.api.v1.chapter import ChapterSchema


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "name": "OWASP Nagoya",
                "country": "America",
                "region": "Europe",
                "created_at": "2024-11-01T00:00:00Z",
                "updated_at": "2024-07-02T00:00:00Z",
            },
            True,
        ),
        (
            {
                "name": "OWASP something",
                "country": "India",
                "region": "Asia",
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-09-02T00:00:00Z",
            },
            True,
        ),
    ],
)
def test_chapter_serializer_validation(data, expected):
    chapter = ChapterSchema(**data)
    assert chapter.name == data["name"]
    assert chapter.country == data["country"]
    assert chapter.region == data["region"]
    assert chapter.created_at == datetime.fromisoformat(data["created_at"])
    assert chapter.updated_at == datetime.fromisoformat(data["updated_at"])
