from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from apps.github.models.issue import Issue
from apps.github.models.repository import Repository
from apps.github.models.user import User


@pytest.fixture
def mock_repository():
    """Return a mock repository."""
    mock_repo = Mock(spec=Repository)
    mock_repo._state = Mock()
    mock_repo.id = 1
    mock_repo.is_fork = False
    mock_repo.is_indexable = True
    mock_repo.track_issues = True
    mock_repo.project.is_documentation_type = False
    mock_repo.project._state = Mock()
    mock_repo.project.track_issues = True
    return mock_repo


@pytest.fixture
def issue(mock_repository):
    """Return an issue instance."""
    return Issue(id=1, title="Test Title", body="Test Body", repository=mock_repository)


class TestIssueModel:
    def test_str(self):
        """Test the string representation of the Issue model."""
        author = User(name="Author", login="author")
        issue = Issue(title="Test Issue", author=author)
        assert str(issue) == "Test Issue by Author (author)"

    def test_open_issues_count(self):
        """Test the open_issues_count method."""
        with patch("apps.github.models.issue.IndexBase.get_total_count") as mock_get_total_count:
            Issue.open_issues_count()
            mock_get_total_count.assert_called_once_with("issues")

    def test_bulk_save(self):
        """Test the bulk_save method."""
        mock_issues = [Mock(id=None), Mock(id=1)]
        with patch("apps.github.models.issue.BulkSaveModel.bulk_save") as mock_bulk_save:
            Issue.bulk_save(mock_issues, fields=["name"])
            mock_bulk_save.assert_called_once_with(Issue, mock_issues, fields=["name"])

    def test_repository_id(self):
        """Test the repository_id property."""
        repository = Repository()
        issue = Issue(repository=repository)
        assert issue.repository_id == repository.id

    @patch("apps.github.models.issue.Issue.objects.get")
    def test_update_data_project_does_not_exist(self, mock_get):
        """Test update_data when the issue does not exist in the database."""
        mock_get.side_effect = Issue.DoesNotExist
        gh_issue_mock = Mock()
        gh_issue_mock.raw_data = {"node_id": "12345"}

        with patch.object(Issue, "save", return_value=None) as mock_save:
            Issue.update_data(gh_issue_mock)
            mock_save.assert_called_once()

    @patch("apps.github.models.issue.OpenAi")
    @patch("apps.github.models.issue.Prompt.get_github_issue_project_summary")
    def test_generate_summary_success(self, mock_get_prompt, mock_openai, issue):
        """Test that generate_summary successfully generates a summary."""
        mock_get_prompt.return_value = "Summarize the following issue"

        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.set_input.return_value = mock_openai_instance
        mock_openai_instance.set_max_tokens.return_value = mock_openai_instance
        mock_openai_instance.set_prompt.return_value = mock_openai_instance
        mock_openai_instance.complete.return_value = "This is a summary."

        issue.generate_summary()

        mock_openai_instance.set_input.assert_called_once_with("Test Title\r\nTest Body")
        mock_openai_instance.set_max_tokens.assert_called_once_with(500)
        mock_openai_instance.set_prompt.assert_called_once_with("Summarize the following issue")
        assert issue.summary == "This is a summary."

    @patch("apps.github.models.issue.Prompt.get_github_issue_project_summary")
    def test_generate_summary_no_prompt(self, mock_get_prompt, issue):
        """Test generate_summary when no prompt is available."""
        mock_get_prompt.return_value = None

        issue.generate_summary()

        assert issue.summary == ""

    @patch("apps.github.models.issue.OpenAi")
    @patch("apps.github.models.issue.Prompt.get_github_issue_project_summary")
    def test_generate_summary_no_content(self, mock_get_prompt, mock_openai, issue):
        """Test generate_summary when the AI returns no content."""
        mock_get_prompt.return_value = "Summarize the following issue"

        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.set_input.return_value = mock_openai_instance
        mock_openai_instance.set_max_tokens.return_value = mock_openai_instance
        mock_openai_instance.set_prompt.return_value = mock_openai_instance
        mock_openai_instance.complete.return_value = ""

        issue.generate_summary()

        assert issue.summary == ""

    @patch("apps.github.models.issue.OpenAi")
    @patch("apps.github.models.issue.Prompt.get_github_issue_hint")
    def test_generate_hint_success(self, mock_get_prompt, mock_openai, issue):
        """Test that generate_hint successfully generates a hint."""
        mock_get_prompt.return_value = "Provide a hint for the following issue"

        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.set_input.return_value = mock_openai_instance
        mock_openai_instance.set_max_tokens.return_value = mock_openai_instance
        mock_openai_instance.set_prompt.return_value = mock_openai_instance
        mock_openai_instance.complete.return_value = "This is a hint."

        issue.generate_hint()

        mock_openai_instance.set_input.assert_called_once_with("Test Title\r\nTest Body")
        mock_openai_instance.set_max_tokens.assert_called_once_with(1000)
        mock_openai_instance.set_prompt.assert_called_once_with(
            "Provide a hint for the following issue"
        )
        assert issue.hint == "This is a hint."

    @patch("apps.github.models.issue.Prompt.get_github_issue_hint")
    def test_generate_hint_no_prompt(self, mock_get_prompt, issue):
        """Test generate_hint when no prompt is available."""
        mock_get_prompt.return_value = None

        issue.generate_hint()

        assert issue.hint == ""

    @patch("apps.github.models.issue.OpenAi")
    @patch("apps.github.models.issue.Prompt.get_github_issue_hint")
    def test_generate_hint_no_content(self, mock_get_prompt, mock_openai, issue):
        """Test generate_hint when the AI returns no content."""
        mock_get_prompt.return_value = "Provide a hint for the following issue"

        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.set_input.return_value = mock_openai_instance
        mock_openai_instance.set_max_tokens.return_value = mock_openai_instance
        mock_openai_instance.set_prompt.return_value = mock_openai_instance
        mock_openai_instance.complete.return_value = ""

        issue.generate_hint()

        assert issue.hint == ""

    def test_from_github_with_none_values(self):
        """Test from_github with None values from the GitHub API."""
        issue = Issue()
        gh_issue = Mock()
        gh_issue.body = None
        gh_issue.comments = None
        gh_issue.closed_at = None
        gh_issue.created_at = None
        gh_issue.locked = None
        gh_issue.active_lock_reason = None
        gh_issue.number = None
        gh_issue.id = None
        gh_issue.state = None
        gh_issue.state_reason = None
        gh_issue.title = None
        gh_issue.updated_at = None
        gh_issue.html_url = None

        issue.from_github(gh_issue)

        assert issue.body == ""
        assert issue.comments_count == 0
        assert issue.closed_at is None
        assert issue.created_at is None
        assert issue.is_locked is False
        assert issue.lock_reason == ""
        assert issue.number == 0
        assert issue.sequence_id == 0
        assert issue.state == "open"
        assert issue.state_reason == ""
        assert issue.title == ""
        assert issue.updated_at is None
        assert issue.url == ""

    @pytest.mark.parametrize(
        ("has_hint", "has_summary"),
        [
            (True, True),
            (False, True),
            (True, False),
            (False, False),
        ],
    )
    def test_save_method(self, has_hint, has_summary, issue):
        """Test the save method."""
        issue.generate_hint = Mock()
        issue.generate_summary = Mock()

        issue.hint = "Test Hint" if has_hint else ""
        issue.summary = "Test Summary" if has_summary else ""

        with patch("apps.github.models.issue.BulkSaveModel.save"):
            issue.save()

        if has_hint:
            issue.generate_hint.assert_not_called()
        else:
            issue.generate_hint.assert_called_once()

        if has_summary:
            issue.generate_summary.assert_not_called()
        else:
            issue.generate_summary.assert_called_once()

    def test_latest_comment_property(self, mock_repository):
        """Test latest_comment property returns the expected query result."""
        issue = Issue(repository=mock_repository)
        
        # Mock the comments queryset
        mock_comments = MagicMock()
        mock_ordered = MagicMock()
        mock_comments.order_by.return_value = mock_ordered
        mock_ordered.first.return_value = None
        
        # Temporarily replace the comments attribute
        issue._state.db = 'default'
        with patch.object(type(issue), 'comments', PropertyMock(return_value=mock_comments)):
            result = issue.latest_comment
            assert result is None
            mock_comments.order_by.assert_called_once_with("-nest_created_at")
            mock_ordered.first.assert_called_once()

    @patch("apps.github.models.issue.Issue.objects.get")
    def test_update_data_without_save(self, mock_get):
        """Test update_data with save=False."""
        existing_issue = Issue(node_id="12345")
        mock_get.return_value = existing_issue
        
        gh_issue_mock = Mock()
        gh_issue_mock.raw_data = {"node_id": "12345"}
        gh_issue_mock.title = "Test Issue"
        gh_issue_mock.body = "Test Body"
        gh_issue_mock.number = 1
        gh_issue_mock.state = "open"
        gh_issue_mock.html_url = "https://github.com/test/issue/1"
        gh_issue_mock.created_at = None
        gh_issue_mock.updated_at = None
        gh_issue_mock.closed_at = None
        gh_issue_mock.comments = 0
        gh_issue_mock.locked = False
        gh_issue_mock.active_lock_reason = None
        gh_issue_mock.state_reason = None
        gh_issue_mock.id = 123

        with (
            patch.object(Issue, "from_github") as mock_from_github,
            patch.object(Issue, "save") as mock_save,
        ):
            result = Issue.update_data(gh_issue_mock, save=False)
            
            mock_from_github.assert_called_once()
            mock_save.assert_not_called()
            assert result == existing_issue
