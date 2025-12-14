import io
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from apps.github.management.commands.github_sync_user import Command
from apps.github.models import User
from apps.github.models.repository import Repository
from apps.owasp.models.member_profile import MemberProfile


class MockPaginatedList:
    """Helper class to mock PyGithub's PaginatedList."""

    def __init__(self, items):
        self._items = items
        self.total_count = len(items)

    def __iter__(self):
        """Return an iterator for the items."""
        return iter(self._items)


@pytest.fixture
def mock_get_github_client():
    with patch("apps.github.management.commands.github_sync_user.get_github_client") as mock:
        yield mock


@pytest.fixture
def mock_gh(mock_get_github_client):
    mock_gh_instance = MagicMock()
    mock_get_github_client.return_value = mock_gh_instance
    return mock_gh_instance


@pytest.fixture
def mock_user():
    with patch("apps.github.management.commands.github_sync_user.User") as mock:
        yield mock


@pytest.fixture
def mock_repo_contributor():
    with patch(
        "apps.github.management.commands.github_sync_user.RepositoryContributor.objects"
    ) as mock:
        yield mock


@pytest.fixture
def mock_org():
    with patch("apps.github.management.commands.github_sync_user.Organization.objects") as mock:
        yield mock


@pytest.fixture
def mock_repo():
    with patch("apps.github.management.commands.github_sync_user.Repository.objects") as mock:
        yield mock


@pytest.fixture
def mock_commit():
    with patch("apps.github.management.commands.github_sync_user.Commit") as mock:
        yield mock


@pytest.fixture
def mock_pr():
    with patch("apps.github.management.commands.github_sync_user.PullRequest") as mock:
        yield mock


@pytest.fixture
def mock_issue():
    with patch("apps.github.management.commands.github_sync_user.Issue") as mock:
        yield mock


@pytest.fixture
def mock_member_profile():
    with patch("apps.github.management.commands.github_sync_user.MemberProfile.objects") as mock:
        yield mock


@pytest.fixture
def default_options():
    """Provide default options for the handle command."""
    return {"username": "testuser", "start_at": None, "end_at": None, "skip_sync": False}


@pytest.fixture
def mock_owasp_org(mock_org):
    """Fixture to mock an OWASP organization query."""
    mock_org_qs = MagicMock()
    mock_org.filter.return_value.distinct.return_value = mock_org_qs
    mock_org_qs.exists.return_value = True
    mock_org_qs.count.return_value = 1
    mock_org_qs.__iter__.return_value = [MagicMock(login="OWASP")]
    return mock_org_qs


def _create_mock_contribution(repo_name, full_name, date, **kwargs):
    """Create a mock contribution object."""
    repo = MagicMock(spec=Repository)
    repo.name = repo_name
    repo.full_name = full_name

    contribution = MagicMock(repository=repo, **kwargs)

    if "commit" in kwargs:
        contribution.commit = MagicMock(author=MagicMock(date=date))
    else:
        contribution.created_at = date

    return contribution


class TestGithubSyncUserCommand:
    @pytest.fixture
    def command(self):
        cmd = Command()
        cmd.stdout = io.StringIO()
        cmd.stderr = io.StringIO()
        return cmd

    def test_parse_date_valid(self, command):
        """Test that a valid date string is parsed correctly."""
        result = command.parse_date("2025-01-15", datetime(2025, 1, 1, tzinfo=UTC))
        assert result == datetime(2025, 1, 15, tzinfo=UTC)

    def test_parse_date_none_returns_default(self, command):
        """Test that a None date string returns the default."""
        default = datetime(2025, 2, 1, tzinfo=UTC)
        result = command.parse_date(None, default)
        assert result == default

    def test_parse_date_invalid_format(self, command):
        """Test that an invalid date string raises ValueError and prints an error."""
        with pytest.raises(ValueError, match=r"time data .* does not match format"):
            command.parse_date("invalid-date", datetime.now(UTC))
        error_output = command.stderr.getvalue()
        assert "Invalid date format" in error_output

    def test_add_arguments(self, command):
        """Test that the command's arguments are correctly added."""
        mock_parser = MagicMock()
        command.add_arguments(mock_parser)
        mock_parser.add_argument.assert_any_call(
            "username", type=str, help="GitHub username to fetch commits, PRs, and issues for"
        )
        mock_parser.add_argument.assert_any_call(
            "--start-at",
            type=str,
            help="Start date (YYYY-MM-DD). Defaults to January 1st of current year.",
        )
        mock_parser.add_argument.assert_any_call(
            "--end-at",
            type=str,
            help="End date (YYYY-MM-DD). Defaults to October 1st of current year.",
        )
        mock_parser.add_argument.assert_any_call(
            "--skip-sync",
            action="store_true",
            help="Skip syncing; only populate first_contribution_at if null",
        )

    def test_handle_user_not_found(self, command, mock_gh):
        """Test that the command handles a GitHub user not found gracefully."""
        mock_gh.get_user.side_effect = GithubException(404, "Not Found")
        options = {
            "username": "unknown_user",
            "start_at": None,
            "end_at": None,
            "skip_sync": False,
        }
        command.handle(**options)
        assert "Could not fetch user unknown_user" in command.stderr.getvalue()

    def test_handle_no_contributions(
        self, command, mock_user, mock_repo_contributor, mock_gh, default_options
    ):
        """Test that the command handles a user with no local contributions."""
        mock_qs = mock_repo_contributor.filter.return_value.select_related.return_value
        mock_qs.exists.return_value = False
        command.handle(**default_options)
        assert "No contributions found for testuser" in command.stderr.getvalue()

    def test_handle_no_owasp_contributions(
        self, command, mock_user, mock_repo_contributor, mock_org, mock_gh, default_options
    ):
        """Test that the command handles a user with no contributions to OWASP-related.

        organizations.
        """
        mock_user_instance = MagicMock(spec=User, id=1, pk=1, username="testuser")
        mock_user.update_data.return_value = mock_user_instance

        mock_contributor_qs = MagicMock()
        mock_repo_contributor.filter.return_value = mock_contributor_qs
        mock_selected_qs = mock_contributor_qs.select_related.return_value
        mock_selected_qs.exists.return_value = True
        mock_contributor_qs.values_list.return_value = [1]

        mock_org.filter.return_value.distinct.return_value.exists.return_value = False

        command.handle(**default_options)
        assert (
            "testuser has no contributions to OWASP-related organizations"
            in command.stderr.getvalue()
        )

    @patch(
        "apps.github.management.commands.github_sync_user.Command.populate_first_contribution_only"
    )
    @patch("apps.github.management.commands.github_sync_user.User.update_data")
    def test_handle_skip_sync(
        self, mock_update_data, mock_populate, command, mock_gh, default_options
    ):
        """Test that the command skips data sync when --skip-sync is used."""
        mock_user_instance = MagicMock(spec=User)
        mock_update_data.return_value = mock_user_instance
        options = {**default_options, "skip_sync": True}
        command.handle(**options)
        assert "Skipping data sync..." in command.stdout.getvalue()
        mock_populate.assert_called_once_with("testuser", mock_user_instance, mock_gh)

    def test_populate_first_contribution_already_set(self, command, mock_member_profile, mock_gh):
        """Test that populate_first_contribution_only skips if date is already set."""
        mock_profile = MagicMock(spec=MemberProfile)
        mock_profile.first_contribution_at = datetime.now(UTC)
        mock_member_profile.get_or_create.return_value = (mock_profile, False)
        command.populate_first_contribution_only("testuser", MagicMock(spec=User), mock_gh)
        assert "First contribution date already set" in command.stdout.getvalue()

    def test_populate_first_contribution_no_owasp_orgs(
        self, command, mock_member_profile, mock_org, mock_gh
    ):
        """Test that populate_first_contribution_only handles no OWASP organizations."""
        mock_profile = MagicMock(spec=MemberProfile, first_contribution_at=None)
        mock_member_profile.get_or_create.return_value = (mock_profile, True)
        mock_org.filter.return_value.exists.return_value = False
        command.populate_first_contribution_only("testuser", MagicMock(spec=User), mock_gh)
        assert "No OWASP organizations found" in command.stderr.getvalue()

    @patch("apps.github.management.commands.github_sync_user.logger")
    @patch("apps.github.management.commands.github_sync_user.User.update_data")
    def test_populate_first_contribution_success_chooses_earliest(
        self, mock_update_data, mock_logger, command, mock_member_profile, mock_org, mock_gh
    ):
        """Test that populate_first_contribution_only correctly chooses the earliest.

        contribution.
        """
        mock_user_instance = MagicMock(spec=User)
        mock_update_data.return_value = mock_user_instance

        mock_profile = MagicMock(spec=MemberProfile, first_contribution_at=None)
        mock_member_profile.get_or_create.return_value = (mock_profile, True)

        mock_org_qs = MagicMock()
        mock_org.filter.return_value = mock_org_qs
        mock_org_qs.exists.return_value = True
        mock_org_qs.__iter__.return_value = [MagicMock(login="OWASP")]

        mock_commit_obj = _create_mock_contribution(
            "commit-repo", "OWASP/commit-repo", datetime(2025, 1, 15, tzinfo=UTC), commit=True
        )
        mock_pr_obj = _create_mock_contribution(
            "pr-repo", "OWASP/pr-repo", datetime(2025, 1, 1, tzinfo=UTC)
        )
        mock_issue_obj = _create_mock_contribution(
            "issue-repo", "OWASP/issue-repo", datetime(2025, 1, 30, tzinfo=UTC)
        )

        mock_gh.search_commits.return_value = MockPaginatedList([mock_commit_obj])
        mock_gh.search_issues.side_effect = [
            MockPaginatedList([mock_pr_obj]),
            MockPaginatedList([mock_issue_obj]),
        ]

        command.populate_first_contribution_only("testuser", mock_user_instance, mock_gh)

        expected_date = datetime(2025, 1, 1, tzinfo=UTC)
        mock_logger.info.assert_called_once_with(
            "Set first OWASP contribution for %s: %s (%s in %s)",
            "testuser",
            expected_date,
            "PR",
            "pr-repo",
        )
        assert mock_profile.first_contribution_at == expected_date
        mock_profile.save.assert_called_once()

    @patch(
        "apps.github.management.commands.github_sync_user.Command.populate_first_contribution_only"
    )
    def test_handle_success(
        self,
        mock_populate,
        command,
        mock_user,
        mock_repo_contributor,
        mock_owasp_org,
        mock_repo,
        mock_commit,
        mock_pr,
        mock_issue,
        mock_gh,
        default_options,
    ):
        mock_repository = MagicMock()
        mock_qs = mock_repo_contributor.filter.return_value
        mock_qs.select_related.return_value.exists.return_value = True
        mock_qs.values_list.return_value = [1]
        mock_repository.owner = MagicMock(login="OWASP")
        mock_repository.name = "test-repo"
        mock_repo.filter.return_value.select_related.return_value = [mock_repository]

        mock_gh_repo = MagicMock(spec=Repository, full_name="OWASP/test-repo")
        mock_gh_commit = MagicMock(repository=mock_gh_repo, sha="123")
        mock_gh.search_commits.return_value = MockPaginatedList([mock_gh_commit])

        mock_gh_pr_search = MagicMock(repository=mock_gh_repo, number=1)
        mock_gh_issue_search = MagicMock(repository=mock_gh_repo, number=2)
        mock_gh.search_issues.side_effect = [
            MockPaginatedList([mock_gh_pr_search]),
            MockPaginatedList([mock_gh_issue_search]),
        ]

        mock_full_gh_repo = MagicMock()
        mock_gh.get_repo.return_value = mock_full_gh_repo
        mock_full_gh_repo.get_pull.return_value = MagicMock()

        command.handle(**default_options)

        output = command.stdout.getvalue()
        assert "Saved 1 commit(s)" in output
        assert "Saved 1 pull request(s)" in output
        assert "Saved 1 issue(s)" in output
        mock_commit.bulk_save.assert_called_once()
        mock_pr.bulk_save.assert_called_once()
        mock_issue.bulk_save.assert_called_once()
        mock_populate.assert_called_once()

    @patch(
        "apps.github.management.commands.github_sync_user.Command.populate_first_contribution_only"
    )
    def test_handle_github_exception_on_commits(
        self,
        mock_populate,
        command,
        mock_user,
        mock_repo_contributor,
        mock_owasp_org,
        mock_repo,
        mock_commit,
        mock_pr,
        mock_issue,
        mock_gh,
        default_options,
    ):
        (
            mock_repo_contributor.filter.return_value.select_related.return_value.exists.return_value
        ) = True
        mock_repo_contributor.filter.return_value.values_list.return_value = [1]

        mock_repo.filter.return_value.select_related.return_value = []
        mock_gh.search_commits.side_effect = GithubException(500, "Server Error")
        mock_gh.search_issues.return_value = MockPaginatedList([])

        command.handle(**default_options)

        assert "Error searching commits in OWASP" in command.stderr.getvalue()
        mock_commit.bulk_save.assert_not_called()
        mock_pr.bulk_save.assert_not_called()
        mock_issue.bulk_save.assert_not_called()

    @patch(
        "apps.github.management.commands.github_sync_user.Command.populate_first_contribution_only"
    )
    def test_handle_no_contributions_in_date_range(
        self,
        mock_populate,
        command,
        mock_user,
        mock_repo_contributor,
        mock_owasp_org,
        mock_repo,
        mock_commit,
        mock_pr,
        mock_issue,
        mock_gh,
        default_options,
    ):
        mock_qs = mock_repo_contributor.filter.return_value
        mock_qs.select_related.return_value.exists.return_value = True
        mock_qs.values_list.return_value = [1]

        mock_repo.filter.return_value.select_related.return_value = []
        mock_gh.search_commits.return_value = MockPaginatedList([])
        mock_gh.search_issues.return_value = MockPaginatedList([])

        command.handle(**default_options)

        assert "No PRs, issues, or commits found for testuser" in command.stdout.getvalue()
        mock_commit.bulk_save.assert_not_called()
        mock_pr.bulk_save.assert_not_called()
        mock_issue.bulk_save.assert_not_called()

    @patch(
        "apps.github.management.commands.github_sync_user.Command.populate_first_contribution_only"
    )
    def test_handle_repository_not_in_cache(
        self,
        mock_populate,
        command,
        mock_user,
        mock_repo_contributor,
        mock_owasp_org,
        mock_repo,
        mock_commit,
        mock_gh,
        default_options,
    ):
        """Test handling when a repository from GitHub is not found in the local cache."""
        (
            mock_repo_contributor.filter.return_value.select_related.return_value.exists.return_value
        ) = True
        mock_repo_contributor.filter.return_value.values_list.return_value = [1]

        mock_repo.filter.return_value.select_related.return_value = []
        mock_gh_commit = MagicMock(repository=MagicMock(full_name="OWASP/un-cached-repo"))
        mock_gh.search_commits.return_value = MockPaginatedList([mock_gh_commit])
        mock_gh.search_issues.return_value = MockPaginatedList([])

        command.handle(**default_options)

        mock_commit.bulk_save.assert_not_called()
        mock_populate.assert_called_once()

    @patch("apps.github.management.commands.github_sync_user.logger")
    def test_populate_first_contribution_no_contributions_found(
        self, mock_logger, command, mock_member_profile, mock_owasp_org, mock_gh
    ):
        """Test that nothing is saved when no contributions are found."""
        mock_profile = MagicMock(spec=MemberProfile, first_contribution_at=None)
        mock_member_profile.get_or_create.return_value = (mock_profile, True)

        mock_gh.search_commits.return_value = MockPaginatedList([])
        mock_gh.search_issues.return_value = MockPaginatedList([])

        command.populate_first_contribution_only("testuser", MagicMock(spec=User), mock_gh)

        mock_profile.save.assert_not_called()
        mock_logger.info.assert_not_called()
        assert "No contributions found for testuser" in command.stdout.getvalue()

    @patch("apps.github.management.commands.github_sync_user.logger")
    def test_populate_first_contribution_partial_github_error(
        self, mock_logger, command, mock_member_profile, mock_owasp_org, mock_gh
    ):
        """Test that the earliest contribution is chosen even if some API calls fail."""
        mock_profile = MagicMock(spec=MemberProfile, first_contribution_at=None)
        mock_member_profile.get_or_create.return_value = (mock_profile, True)

        mock_gh.search_commits.side_effect = GithubException(500, "Server Error")

        mock_pr_obj = _create_mock_contribution(
            "pr-repo", "OWASP/pr-repo", datetime(2025, 1, 1, tzinfo=UTC)
        )
        mock_issue_obj = _create_mock_contribution(
            "issue-repo", "OWASP/issue-repo", datetime(2025, 1, 30, tzinfo=UTC)
        )
        mock_gh.search_issues.side_effect = [
            MockPaginatedList([mock_pr_obj]),
            MockPaginatedList([mock_issue_obj]),
        ]

        command.populate_first_contribution_only("testuser", MagicMock(spec=User), mock_gh)

        expected_date = datetime(2025, 1, 1, tzinfo=UTC)
        mock_logger.info.assert_called_once_with(
            "Set first OWASP contribution for %s: %s (%s in %s)",
            "testuser",
            expected_date,
            "PR",
            "pr-repo",
        )
        assert mock_profile.first_contribution_at == expected_date
        mock_profile.save.assert_called_once()
