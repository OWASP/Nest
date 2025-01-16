from datetime import datetime, timezone

import pytest

from apps.github.models.mixins.repository import RepositoryIndexMixin

CONTRIBUTORS_COUNT = 5
FORKS_COUNT = 5
OPEN_ISSUES_COUNT = 5
STARS_COUNT = 5


class MockModel(RepositoryIndexMixin):
    def __init__(self):
        self.contributors_count = CONTRIBUTORS_COUNT
        self.description = "Description"
        self.forks_count = FORKS_COUNT
        self.languages = ["Python", "JavaScript"]
        self.name = "Name"
        self.open_issues_count = OPEN_ISSUES_COUNT
        self.pushed_at = datetime(2021, 1, 1, tzinfo=timezone.utc)
        self.stars_count = STARS_COUNT
        self.topics = ["Topic1", "Topic2"]
        self.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        self.size = 1024
        self.has_funding_yml = True
        self.license = "MIT"
        self.project = None


class TestRepositoryIndex:
    """Test suite for RepositoryIndexMixin."""

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
    def test_repository_index(self, attr, expected):
        mock_instance = MockModel()
        assert getattr(mock_instance, attr) == expected
