from unittest.mock import Mock, patch

import pytest

from apps.github.models.milestone import Milestone
from apps.github.models.pull_request import PullRequest
from apps.github.models.repository import Repository
from apps.github.models.user import User


@pytest.fixture
def gh_pull_request_mock():
    """Return a mock GitHub pull request object."""
    mock = Mock()
    mock.body = "PR Body"
    mock.closed_at = None
    mock.created_at = "2023-01-01T00:00:00Z"
    mock.merged_at = None
    mock.number = 123
    mock.id = 456
    mock.state = "open"
    mock.title = "PR Title"
    mock.updated_at = "2023-01-01T00:00:00Z"
    mock.html_url = "https://example.com/pr/123"
    mock.raw_data = {"node_id": "pr_node_id_123"}
    return mock


class TestPullRequestModel:
    @pytest.mark.parametrize(
        ("pr_attrs", "related_objects", "expected_attrs"),
        [
            (
                {"state": "open", "merged_at": None},
                {
                    "author": Mock(spec=User, _state=Mock(db=None)),
                    "milestone": None,
                    "repository": Mock(spec=Repository, _state=Mock(db=None)),
                },
                {"state": "open", "merged_at": None},
            ),
            (
                {"state": "closed", "merged_at": "2023-01-02T00:00:00Z"},
                {
                    "author": Mock(spec=User, _state=Mock(db=None)),
                    "milestone": Mock(spec=Milestone, _state=Mock(db=None)),
                    "repository": Mock(spec=Repository, _state=Mock(db=None)),
                },
                {"state": "closed", "merged_at": "2023-01-02T00:00:00Z"},
            ),
            (
                {},
                {
                    "author": None,
                    "milestone": None,
                    "repository": Mock(spec=Repository, _state=Mock(db=None)),
                },
                {"author": None},
            ),
        ],
    )
    def test_from_github(self, gh_pull_request_mock, pr_attrs, related_objects, expected_attrs):
        """Test that from_github correctly maps fields from the GitHub object."""
        for attr, value in pr_attrs.items():
            setattr(gh_pull_request_mock, attr, value)

        pr = PullRequest()
        pr.from_github(gh_pull_request_mock, **related_objects)

        assert pr.body == "PR Body"
        assert pr.number == 123
        assert pr.title == "PR Title"
        assert pr.url == "https://example.com/pr/123"

        for attr, value in expected_attrs.items():
            assert getattr(pr, attr) == value

        assert pr.author is related_objects["author"]
        assert pr.milestone is related_objects["milestone"]
        assert pr.repository is related_objects["repository"]


@patch("apps.github.models.pull_request.BulkSaveModel.bulk_save")
def test_bulk_save(mock_bulk_save):
    """Test that bulk_save calls the parent method correctly."""
    pull_requests = [Mock(spec=PullRequest), Mock(spec=PullRequest)]
    PullRequest.bulk_save(pull_requests, fields=["title"])
    mock_bulk_save.assert_called_once_with(PullRequest, pull_requests, fields=["title"])


@patch("apps.github.models.pull_request.PullRequest.get_node_id")
@patch("apps.github.models.pull_request.PullRequest.objects.get")
def test_update_data_existing_pr(mock_get, mock_get_node_id, gh_pull_request_mock):
    """Test updating an existing pull request."""
    mock_get_node_id.return_value = "pr_node_id_123"
    mock_pr = Mock(spec=PullRequest)
    mock_get.return_value = mock_pr

    author = Mock(spec=User, _state=Mock(db=None))
    milestone = Mock(spec=Milestone, _state=Mock(db=None))
    repository = Mock(spec=Repository, _state=Mock(db=None))

    pr = PullRequest.update_data(
        gh_pull_request_mock,
        author=author,
        milestone=milestone,
        repository=repository,
    )

    mock_get.assert_called_once_with(node_id="pr_node_id_123")
    mock_pr.from_github.assert_called_once_with(
        gh_pull_request_mock,
        author=author,
        milestone=milestone,
        repository=repository,
    )
    mock_pr.save.assert_called_once()
    assert pr == mock_pr


@patch("apps.github.models.pull_request.PullRequest.get_node_id")
@patch("apps.github.models.pull_request.PullRequest.objects.get")
@patch("apps.github.models.pull_request.PullRequest.from_github")
def test_update_data_new_pr(mock_from_github, mock_get, mock_get_node_id, gh_pull_request_mock):
    """Test creating a new pull request."""
    mock_get_node_id.return_value = "pr_node_id_123"
    mock_get.side_effect = PullRequest.DoesNotExist

    author = Mock(spec=User, _state=Mock(db=None))
    milestone = Mock(spec=Milestone, _state=Mock(db=None))
    repository = Mock(spec=Repository, _state=Mock(db=None))

    with patch("apps.github.models.pull_request.PullRequest.save") as mock_save:
        pr = PullRequest.update_data(
            gh_pull_request_mock,
            author=author,
            milestone=milestone,
            repository=repository,
        )

    mock_get.assert_called_once_with(node_id="pr_node_id_123")
    mock_from_github.assert_called_once_with(
        gh_pull_request_mock,
        author=author,
        milestone=milestone,
        repository=repository,
    )
    mock_save.assert_called_once()
    assert pr.node_id == "pr_node_id_123"


def test_pr_save_method():
    """Test the save method."""
    with patch("apps.github.models.generic_issue_model.GenericIssueModel.save") as mock_super_save:
        pr = PullRequest()
        pr.save()
        mock_super_save.assert_called_once_with()


def test_repository_id():
    """Test the repository_id property inherited from GenericIssueModel."""
    repository = Mock(spec=Repository, _state=Mock(db=None))
    repository.id = 999
    pr = PullRequest(repository=repository)
    assert pr.repository_id == 999


@patch("apps.github.models.pull_request.PullRequest.get_node_id")
@patch("apps.github.models.pull_request.PullRequest.objects.get")
def test_update_data_without_save(mock_get, mock_get_node_id, gh_pull_request_mock):
    """Test update_data with save=False."""
    mock_get_node_id.return_value = "pr_node_id_123"
    mock_pr = Mock(spec=PullRequest)
    mock_get.return_value = mock_pr

    author = Mock(spec=User, _state=Mock(db=None))
    milestone = Mock(spec=Milestone, _state=Mock(db=None))
    repository = Mock(spec=Repository, _state=Mock(db=None))

    pr = PullRequest.update_data(
        gh_pull_request_mock,
        author=author,
        milestone=milestone,
        repository=repository,
        save=False,
    )

    mock_get.assert_called_once_with(node_id="pr_node_id_123")
    mock_pr.from_github.assert_called_once_with(
        gh_pull_request_mock,
        author=author,
        milestone=milestone,
        repository=repository,
    )
    mock_pr.save.assert_not_called()
    assert pr == mock_pr
