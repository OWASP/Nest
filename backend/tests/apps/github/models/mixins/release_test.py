from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from apps.github.models.mixins.release import ReleaseIndexMixin


class TestReleaseIndex:
    @pytest.fixture
    def release_index_mixin_instance(self):
        instance = ReleaseIndexMixin()
        instance.author = MagicMock()

        instance.author.avatar_url = "https://example.com/avatar.png"
        instance.author.login = "test_user"
        instance.author.name = "Test User"

        instance.repository = MagicMock(
            path="mock/repository",
            project=MagicMock(nest_key="mock/project"),
        )
        instance.created_at = datetime(2023, 1, 1, tzinfo=UTC)
        instance.published_at = datetime(2023, 6, 1, tzinfo=UTC)
        instance.description = "This is a long description"
        instance.is_pre_release = True
        instance.name = "Release v1.0.0"
        instance.tag_name = "v1.0.0"
        return instance

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            (
                "idx_author",
                [
                    {
                        "avatar_url": "https://example.com/avatar.png",
                        "login": "test_user",
                        "name": "Test User",
                    }
                ],
            ),
            ("idx_created_at", datetime(2023, 1, 1, tzinfo=UTC).timestamp()),
            (
                "idx_description",
                "This is a long description",
            ),
            ("idx_is_pre_release", True),
            ("idx_name", "Release v1.0.0"),
            ("idx_project", "mock/project"),
            ("idx_published_at", datetime(2023, 6, 1, tzinfo=UTC).timestamp()),
            ("idx_repository", "mock/repository"),
            ("idx_tag_name", "v1.0.0"),
            ("idx_author", []),
            ("idx_project", ""),
            ("idx_published_at", None),
        ],
    )
    def test_release_index(self, release_index_mixin_instance, attr, expected):
        if attr == "idx_author" and not expected:
            release_index_mixin_instance.author = None
        elif attr == "idx_project" and expected == "":
            release_index_mixin_instance.repository.project = None
        elif attr == "idx_published_at" and expected is None:
            release_index_mixin_instance.published_at = None
        assert getattr(release_index_mixin_instance, attr) == expected
