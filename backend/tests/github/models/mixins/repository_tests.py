import pytest

from apps.github.models.mixins.repository import RepositoryIndexMixin

CONTRIBUTORS_COUNT = 5
FORKS_COUNT = 5
OPEN_ISSUES_COUNT = 5
STARS_COUNT = 5


class TestRepositoryIndexMixin:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_contributors_count", CONTRIBUTORS_COUNT),
            ("idx_description", "Description"),
            ("idx_forks_count", FORKS_COUNT),
            ("idx_languages", ["Python", "JavaScript"]),
            ("idx_name", "Name"),
            ("idx_open_issues_count", OPEN_ISSUES_COUNT),
            ("idx_pushed_at", "2021-01-01"),
            ("idx_stars_count", STARS_COUNT),
            ("idx_topics", ["Topic1", "Topic2"]),
        ],
    )
    def test_repository_index(self, attr, expected):
        class MockModel(RepositoryIndexMixin):
            def __init__(self):
                self.contributors_count = 5
                self.description = "Description"
                self.forks_count = 5
                self.top_languages = ["Python", "JavaScript"]
                self.name = "Name"
                self.open_issues_count = 5
                self.pushed_at = "2021-01-01"
                self.stars_count = 5
                self.topics = ["Topic1", "Topic2"]

        mock_instance = MockModel()

        assert getattr(mock_instance, attr) == expected
