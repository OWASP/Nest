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
            "latitude": 35.1815,
            "longitude": 136.9066,
            "name": "OWASP Nagoya",
            "region": "Europe",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "country": "India",
            "created_at": "2023-12-01T00:00:00Z",
            "key": "something",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "name": "OWASP something",
            "region": "Asia",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_chapter_serializer_validation(chapter_data):
    class MockEntityMember:
        def __init__(self, name):
            self.member_name = name

    class MockChapter:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]
            self.entity_leaders = [MockEntityMember("Alice"), MockEntityMember("Bob")]

    chapter = ChapterDetail.from_orm(MockChapter(chapter_data))

    assert chapter.country == chapter_data["country"]
    assert chapter.created_at == datetime.fromisoformat(chapter_data["created_at"])
    assert chapter.key == chapter_data["key"]
    assert chapter.latitude == chapter_data["latitude"]
    assert chapter.longitude == chapter_data["longitude"]
    assert chapter.leaders == ["Alice", "Bob"]
    assert chapter.name == chapter_data["name"]
    assert chapter.region == chapter_data["region"]
    assert chapter.updated_at == datetime.fromisoformat(chapter_data["updated_at"])
