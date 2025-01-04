from unittest.mock import MagicMock

from apps.github.models.mixins.issue import IssueIndexMixin

CONTRIBUTORS_COUNT = 10
FORKS_COUNT = 5
STARS_COUNT = 50
COMMENTS_COUNT = 5


class TestIssueIndexMixin:
    def test_issue_index(self):
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
                self.comments_count = 5
                self.created_at = "2021-09-01T00:00:00Z"
                self.updated_at = "2021-09-02T00:00:00Z"
                self.url = "https://example.com/issue"
                self.title = "Issue Title"
                self.summary = "Issue Summary"
                self.hint = "Issue Hint"
                self.labels = MagicMock(all=lambda: [mock_label_1, mock_label_2])

        mock_instance = MockModel()

        assert isinstance(mock_instance, IssueIndexMixin)

        assert mock_instance.idx_author_login == "test_user"
        assert mock_instance.idx_author_name == "Test User"

        assert mock_instance.idx_project_description == "Project description"
        assert mock_instance.idx_project_level == "High"
        assert mock_instance.idx_project_tags == ["tag1", "tag2"]
        assert mock_instance.idx_project_topics == ["topic1", "topic2"]
        assert mock_instance.idx_project_name == "Project Name"
        assert mock_instance.idx_project_url == "https://example.com/project"

        assert mock_instance.idx_repository_contributors_count == CONTRIBUTORS_COUNT
        assert mock_instance.idx_repository_description == "Repository description"
        assert mock_instance.idx_repository_forks_count == FORKS_COUNT
        assert mock_instance.idx_repository_languages == ["Python", "JavaScript"]
        assert mock_instance.idx_repository_name == "Repository Name"
        assert mock_instance.idx_repository_stars_count == STARS_COUNT
        assert mock_instance.idx_repository_topics == ["repo_topic1", "repo_topic2"]

        assert mock_instance.idx_labels == ["bug", "feature"]

        assert mock_instance.idx_comments_count == COMMENTS_COUNT
        assert mock_instance.idx_created_at == "2021-09-01T00:00:00Z"
        assert mock_instance.idx_updated_at == "2021-09-02T00:00:00Z"
        assert mock_instance.idx_url == "https://example.com/issue"
        assert mock_instance.idx_title == "Issue Title"
        assert mock_instance.idx_summary == "Issue Summary"
        assert mock_instance.idx_hint == "Issue Hint"
