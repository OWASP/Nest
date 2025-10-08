from datetime import datetime

import pytest

from apps.api.rest.v0.release import ReleaseDetail


class TestReleaseSchema:
    @pytest.mark.parametrize(
        "release_data",
        [
            {
                "created_at": "2024-12-30T00:00:00Z",
                "description": "First stable release",
                "name": "v1.0",
                "published_at": "2024-12-30T00:00:00Z",
                "tag_name": "v1.0.0",
            },
            {
                "created_at": "2024-12-29T00:00:00Z",
                "description": "Minor improvements and bug fixes",
                "name": "v1.1",
                "published_at": "2024-12-30T00:00:00Z",
                "tag_name": "v1.1.0",
            },
        ],
    )
    def test_release_schema(self, release_data):
        release = ReleaseDetail(**release_data)

        assert release.created_at == datetime.fromisoformat(release_data["created_at"])
        assert release.description == release_data["description"]
        assert release.name == release_data["name"]
        assert release.published_at == datetime.fromisoformat(release_data["published_at"])
        assert release.tag_name == release_data["tag_name"]
