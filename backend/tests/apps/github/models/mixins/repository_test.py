from datetime import datetime, timezone

import pytest

from apps.github.models.mixins.repository import RepositoryIndexMixin
from apps.github.models.release import Release

CONTRIBUTORS_COUNT = 5
FORKS_COUNT = 5
OPEN_ISSUES_COUNT = 5
STARS_COUNT = 5


@pytest.fixture
def repository_index_mixin_instance():
    instance = RepositoryIndexMixin()
    instance.contributors_count = CONTRIBUTORS_COUNT
    instance.description = "Description"
    instance.forks_count = FORKS_COUNT
    instance.languages = ["Python", "JavaScript"]
    instance.name = "Name"
    instance.open_issues_count = OPEN_ISSUES_COUNT
    instance.pushed_at = datetime(2021, 1, 1, tzinfo=timezone.utc)
    instance.stars_count = STARS_COUNT
    instance.topics = ["Topic1", "Topic2"]
    instance.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    instance.size = 1024
    instance.has_funding_yml = True
    instance.license = "MIT"
    instance.project = None
    return instance


class TestRepositoryIndexMixin:
    """Test suite for RepositoryIndexMixin."""

    @pytest.mark.parametrize(
        ("is_draft", "expected_indexable"),
        [
            (False, True),
            (True, False),
        ],
    )
    def test_is_indexable(self, is_draft, expected_indexable):
        release = Release(is_draft=is_draft)
        assert release.is_indexable == expected_indexable

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_contributors_count", CONTRIBUTORS_COUNT),
            ("idx_description", "Description"),
            ("idx_forks_count", FORKS_COUNT),
            ("idx_languages", ["Python", "JavaScript"]),
            ("idx_name", "Name"),
            ("idx_open_issues_count", OPEN_ISSUES_COUNT),
            ("idx_pushed_at", datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp()),
            ("idx_stars_count", STARS_COUNT),
            ("idx_topics", ["Topic1", "Topic2"]),
        ],
    )
    def test_repository_index(self, repository_index_mixin_instance, attr, expected):
        assert getattr(repository_index_mixin_instance, attr) == expected
