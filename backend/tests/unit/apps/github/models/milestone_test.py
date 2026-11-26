from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from apps.github.models.milestone import Milestone
from apps.github.models.repository import Repository
from apps.github.models.user import User


@pytest.fixture
def gh_milestone_mock():
    """Return a mock GitHub milestone object."""
    mock = Mock()
    mock.description = "Milestone description"
    mock.closed_at = None
    mock.closed_issues = 0
    mock.created_at = "2023-01-01T00:00:00Z"
    mock.due_on = "2023-02-01T00:00:00Z"
    mock.number = 1
    mock.open_issues = 10
    mock.state = "open"
    mock.title = "Milestone Title"
    mock.updated_at = "2023-01-01T00:00:00Z"
    mock.html_url = "https://example.com/milestone/1"
    mock.raw_data = {"node_id": "milestone_node_id_1"}
    return mock


class TestMilestoneModel:
    def test_from_github(self, gh_milestone_mock):
        """Test that from_github correctly maps fields from the GitHub object."""
        milestone = Milestone()
        author = Mock(spec=User, _state=Mock(db=None))
        repository = Mock(spec=Repository, _state=Mock(db=None))

        milestone.from_github(gh_milestone_mock, author=author, repository=repository)

        assert milestone.body == "Milestone description"
        assert milestone.closed_issues_count == 0
        assert milestone.open_issues_count == 10
        assert milestone.number == 1
        assert milestone.title == "Milestone Title"
        assert milestone.url == "https://example.com/milestone/1"
        assert milestone.author == author
        assert milestone.repository == repository

    @pytest.mark.parametrize("due_on", [None, datetime(2027, 1, 1, tzinfo=UTC)])
    def test_from_github_updates_due_date(self, gh_milestone_mock, due_on):
        """Sync a removed or replaced due date without clearing other fields."""
        milestone = Milestone(
            due_on=datetime(2026, 12, 1, tzinfo=UTC),
            title="Keep this title",
            body="Keep this body",
        )
        gh_milestone_mock.due_on = due_on
        gh_milestone_mock.title = None
        gh_milestone_mock.description = None

        milestone.from_github(gh_milestone_mock)

        assert milestone.due_on == due_on
        assert milestone.title == "Keep this title"
        assert milestone.body == "Keep this body"

    def test_from_github_repeated_null_due_date(self, gh_milestone_mock):
        """A milestone without a due date stays undated across syncs."""
        milestone = Milestone(due_on=None)
        gh_milestone_mock.due_on = None

        milestone.from_github(gh_milestone_mock)
        milestone.from_github(gh_milestone_mock)

        assert milestone.due_on is None

    @patch("apps.github.models.milestone.Milestone.objects.get")
    @patch("apps.github.models.milestone.Milestone.save")
    def test_update_data_clears_due_date(self, mock_save, mock_get, gh_milestone_mock):
        """Update the existing milestone and pass the cleared date to save."""
        milestone = Milestone(due_on=datetime(2026, 12, 1, tzinfo=UTC))
        mock_get.return_value = milestone
        gh_milestone_mock.due_on = None

        result = Milestone.update_data(gh_milestone_mock)

        assert result is milestone
        assert result.due_on is None
        mock_get.assert_called_once_with(node_id="milestone_node_id_1")
        mock_save.assert_called_once_with()

    @patch("apps.github.models.milestone.BulkSaveModel.bulk_save")
    def test_bulk_save(self, mock_bulk_save):
        """Test that bulk_save calls the parent method correctly."""
        milestones = [Mock(spec=Milestone), Mock(spec=Milestone)]
        Milestone.bulk_save(milestones, fields=["title"])
        mock_bulk_save.assert_called_once_with(Milestone, milestones, fields=["title"])

    @patch("apps.github.models.milestone.Milestone.get_node_id")
    @patch("apps.github.models.milestone.Milestone.objects.get")
    def test_update_data_existing_milestone(self, mock_get, mock_get_node_id, gh_milestone_mock):
        """Test updating an existing milestone."""
        mock_get_node_id.return_value = "milestone_node_id_1"
        mock_milestone = Mock(spec=Milestone)
        mock_get.return_value = mock_milestone

        author = Mock(spec=User, _state=Mock(db=None))
        repository = Mock(spec=Repository, _state=Mock(db=None))

        milestone = Milestone.update_data(gh_milestone_mock, author=author, repository=repository)

        mock_get.assert_called_once_with(node_id="milestone_node_id_1")
        mock_milestone.from_github.assert_called_once_with(gh_milestone_mock, author, repository)
        mock_milestone.save.assert_called_once()
        assert milestone == mock_milestone

    @patch("apps.github.models.milestone.Milestone.get_node_id")
    @patch("apps.github.models.milestone.Milestone.objects.get")
    @patch("apps.github.models.milestone.Milestone.from_github")
    def test_update_data_new_milestone(
        self, mock_from_github, mock_get, mock_get_node_id, gh_milestone_mock
    ):
        """Test creating a new milestone."""
        mock_get_node_id.return_value = "milestone_node_id_1"
        mock_get.side_effect = Milestone.DoesNotExist

        author = Mock(spec=User, _state=Mock(db=None))
        repository = Mock(spec=Repository, _state=Mock(db=None))

        with patch("apps.github.models.milestone.Milestone.save") as mock_save:
            milestone = Milestone.update_data(
                gh_milestone_mock, author=author, repository=repository
            )

        mock_get.assert_called_once_with(node_id="milestone_node_id_1")
        mock_from_github.assert_called_once_with(gh_milestone_mock, author, repository)
        mock_save.assert_called_once()
        assert milestone.node_id == "milestone_node_id_1"

    @patch("apps.github.models.milestone.Milestone.get_node_id")
    @patch("apps.github.models.milestone.Milestone.objects.get")
    def test_update_data_without_save(self, mock_get, mock_get_node_id, gh_milestone_mock):
        """Test update_data with save=False."""
        mock_get_node_id.return_value = "milestone_node_id_1"
        mock_milestone = Mock(spec=Milestone)
        mock_get.return_value = mock_milestone

        author = Mock(spec=User, _state=Mock(db=None))
        repository = Mock(spec=Repository, _state=Mock(db=None))

        milestone = Milestone.update_data(
            gh_milestone_mock, author=author, repository=repository, save=False
        )

        mock_get.assert_called_once_with(node_id="milestone_node_id_1")
        mock_milestone.from_github.assert_called_once_with(gh_milestone_mock, author, repository)
        mock_milestone.save.assert_not_called()
        assert milestone == mock_milestone
