from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from apps.github.models.mixins.issue import IssueIndexMixin

COMMENTS_COUNT = 5
FOLLOWERS_COUNT = 10
FORKS_COUNT = 3
STARS_COUNT = 100


@pytest.fixture
def issue_index_mixin_instance():
    instance = IssueIndexMixin()
    instance.author = MagicMock()
    instance.author.login = "test_user"
    instance.author.name = "Test User"

    instance.project = MagicMock()
    instance.project.idx_description = "Project description"
    instance.project.idx_level = "High"
    instance.project.idx_level_raw = "high_level"
    instance.project.idx_tags = ["tag1", "tag2"]
    instance.project.idx_topics = ["topic1", "topic2"]
    instance.project.idx_name = "Project Name"
    instance.project.idx_url = "https://example.com/project"

    instance.repository = MagicMock()
    instance.repository.idx_contributors_count = FOLLOWERS_COUNT
    instance.repository.idx_description = "Repository description"
    instance.repository.idx_forks_count = FORKS_COUNT
    instance.repository.idx_name = "Repository Name"
    instance.repository.idx_stars_count = STARS_COUNT
    instance.repository.idx_topics = ["repo_topic1", "repo_topic2"]
    instance.repository.top_languages = ["Python", "JavaScript"]

    mock_label1 = MagicMock()
    mock_label1.name = "bug"
    mock_label2 = MagicMock()
    mock_label2.name = "feature"

    instance.labels = MagicMock()
    instance.labels.all.return_value = [mock_label1, mock_label2]

    instance.comments_count = COMMENTS_COUNT
    instance.created_at = datetime(2021, 9, 1, tzinfo=UTC)
    instance.updated_at = datetime(2021, 9, 2, tzinfo=UTC)
    instance.url = "https://example.com/issue"
    instance.title = "Issue Title"
    instance.summary = "Issue Summary"
    instance.hint = "Issue Hint"
    return instance


class TestIssueIndexMixin:
    """Test suite for IssueIndexMixin."""

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_author_login", "test_user"),
            ("idx_author_name", "Test User"),
            ("idx_labels", ["bug", "feature"]),
            ("idx_project_description", "Project description"),
            ("idx_project_level", "High"),
            ("idx_project_level_raw", "high_level"),
            ("idx_project_tags", ["tag1", "tag2"]),
            ("idx_project_topics", ["topic1", "topic2"]),
            ("idx_project_name", "Project Name"),
            ("idx_project_url", "https://example.com/project"),
            ("idx_repository_contributors_count", FOLLOWERS_COUNT),
            ("idx_repository_languages", ["Python", "JavaScript"]),
            ("idx_repository_description", "Repository description"),
            ("idx_repository_forks_count", FORKS_COUNT),
            ("idx_repository_name", "Repository Name"),
            ("idx_repository_stars_count", STARS_COUNT),
            ("idx_repository_topics", ["repo_topic1", "repo_topic2"]),
            ("idx_comments_count", COMMENTS_COUNT),
            ("idx_created_at", datetime(2021, 9, 1, tzinfo=UTC).timestamp()),
            ("idx_updated_at", datetime(2021, 9, 2, tzinfo=UTC).timestamp()),
            ("idx_url", "https://example.com/issue"),
            ("idx_title", "Issue Title"),
            ("idx_summary", "Issue Summary"),
            ("idx_hint", "Issue Hint"),
        ],
    )
    def test_issue_index(self, issue_index_mixin_instance, attr, expected):
        assert getattr(issue_index_mixin_instance, attr) == expected
