from datetime import datetime

import pytest

from apps.github.api.v1.release import ReleaseSchema


class TestReleaseSchema:
    @pytest.mark.parametrize(
        "release_data",
        [
            {
                "name": "v1.0",
                "tag_name": "v1.0.0",
                "description": "First stable release",
                "created_at": "2024-12-30T00:00:00Z",
                "published_at": "2024-12-30T00:00:00Z",
            },
            {
                "name": "v1.1",
                "tag_name": "v1.1.0",
                "description": "Minor improvements and bug fixes",
                "created_at": "2024-12-29T00:00:00Z",
                "published_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_release_schema(self, release_data):
        schema = ReleaseSchema(**release_data)
        assert schema.created_at == datetime.fromisoformat(release_data["created_at"])
        assert schema.published_at == datetime.fromisoformat(release_data["published_at"])

        assert schema.name == release_data["name"]
        assert schema.tag_name == release_data["tag_name"]
        assert schema.description == release_data["description"]
