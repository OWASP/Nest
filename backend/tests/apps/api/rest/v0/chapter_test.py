from datetime import datetime

import pytest

from apps.api.rest.v0.chapter import ChapterDetail


@pytest.mark.parametrize(
    "chapter_data",
    [
        {
            "country": "America",
            "created_at": "2024-11-01T00:00:00Z",
            "key": "nagoya",
            "name": "OWASP Nagoya",
            "longitude": 136.9066,
            "latitude": 35.1815,
            "region": "Europe",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "country": "India",
            "created_at": "2023-12-01T00:00:00Z",
            "key": "something",
            "name": "OWASP something",
            "longitude": 77.5946,
            "latitude": 12.9716,
            "region": "Asia",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_chapter_serializer_validation(chapter_data):
    class MockChapter:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    chapter = ChapterDetail.from_orm(MockChapter(chapter_data))

    assert chapter.country == chapter_data["country"]
    assert chapter.created_at == datetime.fromisoformat(chapter_data["created_at"])
    assert chapter.key == chapter_data["key"]
    assert chapter.name == chapter_data["name"]
    assert chapter.region == chapter_data["region"]
    assert chapter.updated_at == datetime.fromisoformat(chapter_data["updated_at"])
    assert chapter.longitude == chapter_data["longitude"]
    assert chapter.latitude == chapter_data["latitude"]
