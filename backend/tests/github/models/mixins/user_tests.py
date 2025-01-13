from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from apps.github.models.mixins.issue import IssueIndexMixin

COMMENTS_COUNT = 5
FOLLOWERS_COUNT = 10
FORKS_COUNT = 3
STARS_COUNT = 100


class MockModel(IssueIndexMixin):
    def __init__(self):
        self.author = MagicMock()
        self.author.login = "test_user"
        self.author.name = "Test User"

        self.project = MagicMock()
        self.project.idx_description = "Project description"
        self.project.idx_level = "High"
        self.project.idx_tags = ["tag1", "tag2"]
        self.project.idx_topics = ["topic1", "topic2"]
        self.project.idx_name = "Project Name"
        self.project.idx_url = "https://example.com/project"

        self.repository = MagicMock()
        self.repository.idx_contributors_count = FOLLOWERS_COUNT
        self.repository.idx_description = "Repository description"
        self.repository.idx_forks_count = FORKS_COUNT
        self.repository.idx_languages = ["Python", "JavaScript"]
        self.repository.idx_name = "Repository Name"
        self.repository.idx_stars_count = STARS_COUNT
        self.repository.idx_topics = ["repo_topic1", "repo_topic2"]

        self.comments_count = COMMENTS_COUNT
        self.created_at = datetime(2021, 9, 1, tzinfo=timezone.utc)
        self.updated_at = datetime(2021, 9, 2, tzinfo=timezone.utc)
        self.url = "https://example.com/issue"
        self.title = "Issue Title"
        self.summary = "Issue Summary"
        self.hint = "Issue Hint"
        self.labels = MagicMock(all=lambda: [MagicMock(name="bug"), MagicMock(name="feature")])


class TestIssueIndexMixin:
    """Test suite for IssueIndexMixin."""

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_author_login", "test_user"),
            ("idx_author_name", "Test User"),
            ("idx_project_description", "Project description"),
            ("idx_project_level", "High"),
            ("idx_project_tags", ["tag1", "tag2"]),
            ("idx_project_topics", ["topic1", "topic2"]),
            ("idx_project_name", "Project Name"),
            ("idx_project_url", "https://example.com/project"),
            ("idx_repository_contributors_count", FOLLOWERS_COUNT),
            ("idx_repository_description", "Repository description"),
            ("idx_repository_forks_count", FORKS_COUNT),
            ("idx_repository_languages", ["Python", "JavaScript"]),
            ("idx_repository_name", "Repository Name"),
            ("idx_repository_stars_count", STARS_COUNT),
            ("idx_repository_topics", ["repo_topic1", "repo_topic2"]),
            ("idx_comments_count", COMMENTS_COUNT),
            ("idx_created_at", datetime(2021, 9, 1, tzinfo=timezone.utc).timestamp()),
            ("idx_updated_at", datetime(2021, 9, 2, tzinfo=timezone.utc).timestamp()),
            ("idx_url", "https://example.com/issue"),
            ("idx_title", "Issue Title"),
            ("idx_summary", "Issue Summary"),
            ("idx_hint", "Issue Hint"),
        ],
    )
    def test_issue_index(self, attr, expected):
        mock_instance = MockModel()
        assert getattr(mock_instance, attr) == expected
