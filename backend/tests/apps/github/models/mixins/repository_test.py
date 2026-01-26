from datetime import UTC, datetime

import pytest

from apps.github.models.mixins.repository import RepositoryIndexMixin
from apps.github.models.release import Release

CONTRIBUTORS_COUNT = 5
FORKS_COUNT = 5
OPEN_ISSUES_COUNT = 5
STARS_COUNT = 5
SUBSCRIBERS_COUNT = 10


@pytest.fixture
def repository_index_mixin_instance():
    instance = RepositoryIndexMixin()
    instance.commits_count = 100
    instance.contributors_count = CONTRIBUTORS_COUNT
    instance.created_at = datetime(2020, 1, 1, tzinfo=UTC)
    instance.description = "Description"
    instance.forks_count = FORKS_COUNT
    instance.has_funding_yml = True
    instance.languages = ["Python", "JavaScript"]
    instance.license = "MIT"
    instance.name = "Name"
    instance.nest_key = "nest/key"
    instance.open_issues_count = OPEN_ISSUES_COUNT
    instance.project = None
    instance.pushed_at = datetime(2021, 1, 1, tzinfo=UTC)
    instance.size = 1024
    instance.stars_count = STARS_COUNT
    instance.subscribers_count = SUBSCRIBERS_COUNT
    instance.topics = ["Topic1", "Topic2"]
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
        ("is_archived", "is_empty", "is_template", "project_exists", "expected"),
        [
            (False, False, False, True, True),
            (True, False, False, True, False),
            (False, True, False, True, False),
            (False, False, True, True, False),
            (False, False, False, False, False),
        ],
    )
    def test_is_indexable_for_repository(
        self,
        repository_index_mixin_instance,
        is_archived,
        is_empty,
        is_template,
        project_exists,
        expected,
    ):
        """Tests the is_indexable property under various conditions.

        (archived, empty, template, project existence).
        """
        repository_index_mixin_instance.is_archived = is_archived
        repository_index_mixin_instance.is_empty = is_empty
        repository_index_mixin_instance.is_template = is_template
        repository_index_mixin_instance.project_set = lambda: None
        repository_index_mixin_instance.project_set.exists = lambda: project_exists
        assert repository_index_mixin_instance.is_indexable == expected

    def test_idx_project_key(self, repository_index_mixin_instance, mocker):
        """Tests the idx_project_key property with and without an associated project."""
        # Case 1: Project exists
        mock_project = mocker.Mock()
        mock_project.nest_key = "project_key"
        repository_index_mixin_instance.project = mock_project
        assert repository_index_mixin_instance.idx_project_key == "project_key"

        # Case 2: Project does not exist
        repository_index_mixin_instance.project = None
        assert repository_index_mixin_instance.idx_project_key == ""

    def test_idx_top_contributors(self, repository_index_mixin_instance, mocker):
        """Tests the idx_top_contributors property by mocking the get_top_contributors method."""
        mock_get_top_contributors = mocker.patch(
            "apps.github.models.repository_contributor.RepositoryContributor.get_top_contributors"
        )
        expected_contributors = [{"login": "testuser", "contributions": 100}]
        mock_get_top_contributors.return_value = expected_contributors

        repository_index_mixin_instance.key = "repo_key"
        assert repository_index_mixin_instance.idx_top_contributors == expected_contributors
        mock_get_top_contributors.assert_called_once_with(repository="repo_key")

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_commits_count", 100),
            ("idx_contributors_count", CONTRIBUTORS_COUNT),
            ("idx_created_at", datetime(2020, 1, 1, tzinfo=UTC).timestamp()),
            ("idx_description", "Description"),
            ("idx_forks_count", FORKS_COUNT),
            ("idx_has_funding_yml", True),
            ("idx_key", "nest/key"),
            ("idx_languages", ["Python", "JavaScript"]),
            ("idx_license", "MIT"),
            ("idx_name", "Name"),
            ("idx_open_issues_count", OPEN_ISSUES_COUNT),
            ("idx_pushed_at", datetime(2021, 1, 1, tzinfo=UTC).timestamp()),
            ("idx_size", 1024),
            ("idx_stars_count", STARS_COUNT),
            ("idx_subscribers_count", SUBSCRIBERS_COUNT),
            ("idx_topics", ["Topic1", "Topic2"]),
        ],
    )
    def test_repository_index(self, repository_index_mixin_instance, attr, expected):
        """Tests various simple repository index properties."""
        assert getattr(repository_index_mixin_instance, attr) == expected
