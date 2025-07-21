from datetime import datetime

import pytest

from apps.owasp.api.rest.v1.chapter import ChapterSchema


@pytest.mark.parametrize(
    "chapter_data",
    [
        {
            "name": "OWASP Nagoya",
            "country": "America",
            "region": "Europe",
            "created_at": "2024-11-01T00:00:00Z",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "name": "OWASP something",
            "country": "India",
            "region": "Asia",
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_chapter_serializer_validation(chapter_data):
    chapter = ChapterSchema(**chapter_data)
    assert chapter.name == chapter_data["name"]
    assert chapter.country == chapter_data["country"]
    assert chapter.region == chapter_data["region"]
    assert chapter.created_at == datetime.fromisoformat(chapter_data["created_at"])
    assert chapter.updated_at == datetime.fromisoformat(chapter_data["updated_at"])
