from unittest.mock import MagicMock

import pytest

from apps.github.models.mixins.issue import IssueIndexMixin

CONTRIBUTORS_COUNT = 10
FORKS_COUNT = 5
STARS_COUNT = 50
COMMENTS_COUNT = 5


class TestIssueIndexMixin:
    @pytest.fixture()
    def mock_model(self):
        mock_author = MagicMock()
        mock_author.login = "test_user"
        mock_author.name = "Test User"

        mock_project = MagicMock()
        mock_project.idx_description = "Project description"
        mock_project.idx_level = "High"
        mock_project.idx_tags = ["tag1", "tag2"]
        mock_project.idx_topics = ["topic1", "topic2"]
        mock_project.idx_name = "Project Name"
        mock_project.idx_url = "https://example.com/project"

        mock_repository = MagicMock()
        mock_repository.idx_contributors_count = CONTRIBUTORS_COUNT
        mock_repository.idx_description = "Repository description"
        mock_repository.idx_forks_count = FORKS_COUNT
        mock_repository.idx_languages = ["Python", "JavaScript"]
        mock_repository.idx_name = "Repository Name"
        mock_repository.idx_stars_count = STARS_COUNT
        mock_repository.idx_topics = ["repo_topic1", "repo_topic2"]

        mock_label_1 = MagicMock()
        mock_label_1.name = "bug"
        mock_label_2 = MagicMock()
        mock_label_2.name = "feature"

        class MockModel(IssueIndexMixin):
            def __init__(self):
                self.author = mock_author
                self.project = mock_project
                self.repository = mock_repository
                self.comments_count = COMMENTS_COUNT
                self.created_at = "2021-09-01T00:00:00Z"
                self.updated_at = "2021-09-02T00:00:00Z"
                self.url = "https://example.com/issue"
                self.title = "Issue Title"
                self.summary = "Issue Summary"
                self.hint = "Issue Hint"
                self.labels = MagicMock(all=lambda: [mock_label_1, mock_label_2])

        return MockModel()

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
            ("idx_repository_contributors_count", CONTRIBUTORS_COUNT),
            ("idx_repository_description", "Repository description"),
            ("idx_repository_forks_count", FORKS_COUNT),
            ("idx_repository_languages", ["Python", "JavaScript"]),
            ("idx_repository_name", "Repository Name"),
            ("idx_repository_stars_count", STARS_COUNT),
            ("idx_repository_topics", ["repo_topic1", "repo_topic2"]),
            ("idx_labels", ["bug", "feature"]),
            ("idx_comments_count", COMMENTS_COUNT),
            ("idx_created_at", "2021-09-01T00:00:00Z"),
            ("idx_updated_at", "2021-09-02T00:00:00Z"),
            ("idx_url", "https://example.com/issue"),
            ("idx_title", "Issue Title"),
            ("idx_summary", "Issue Summary"),
            ("idx_hint", "Issue Hint"),
        ],
    )
    def test_issue_index(self, mock_model, attr, expected):
        assert getattr(mock_model, attr) == expected
