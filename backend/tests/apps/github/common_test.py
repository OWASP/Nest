from datetime import timedelta as td
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from github.GithubException import UnknownObjectException

from apps.github.common import sync_repository


@pytest.fixture
def mock_common_deps(mocker):
    """Mocks all dependencies for the sync_repository function."""
    mocks = {
        "Organization": mocker.patch("apps.github.common.Organization"),
        "User": mocker.patch("apps.github.common.User"),
        "Repository": mocker.patch("apps.github.common.Repository"),
        "Milestone": mocker.patch("apps.github.common.Milestone"),
        "Issue": mocker.patch("apps.github.common.Issue"),
        "PullRequest": mocker.patch("apps.github.common.PullRequest"),
        "Label": mocker.patch("apps.github.common.Label"),
        "Release": mocker.patch("apps.github.common.Release"),
        "RepositoryContributor": mocker.patch("apps.github.common.RepositoryContributor"),
        "check_owasp": mocker.patch(
            "apps.github.common.check_owasp_site_repository", return_value=False
        ),
        "logger": mocker.patch("apps.github.common.logger"),
    }

    mock_repository = mocks["Repository"].update_data.return_value
    mock_repository.is_archived = False
    mock_repository.track_issues = True
    mock_repository.project.track_issues = True
    mock_repository.latest_updated_milestone = None
    mock_repository.latest_updated_issue = None
    mock_repository.latest_updated_pull_request = None
    mock_repository.id = 1

    yield mocks


@pytest.fixture
def mock_gh_repository():
    """Provides a mock GitHub repository object from the pygithub library."""
    gh_repo = MagicMock(name="gh_repository")
    gh_repo.name = "test-repo"
    gh_repo.organization = MagicMock(name="gh_organization")
    gh_repo.owner = MagicMock(name="gh_owner")
    gh_repo.get_commits.return_value = []
    gh_repo.get_contributors.return_value = []
    gh_repo.get_languages.return_value = {}
    gh_repo.get_milestones.return_value = []
    gh_repo.get_issues.return_value = []
    gh_repo.get_pulls.return_value = []
    gh_repo.get_releases.return_value = []
    return gh_repo


class TestSyncRepository:

    def test_basic_flow(self, mock_common_deps, mock_gh_repository):
        """Tests the basic successful execution of sync_repository."""
        org, repo = sync_repository(mock_gh_repository)

        mock_common_deps["Organization"].update_data.assert_called_once_with(
            mock_gh_repository.organization
        )
        mock_common_deps["User"].update_data.assert_called_once_with(mock_gh_repository.owner)
        mock_common_deps["Repository"].update_data.assert_called_once()
        mock_gh_repository.get_languages.assert_called_once()
        mock_gh_repository.get_releases.assert_called_once()
        mock_common_deps["Release"].bulk_save.assert_called_once()
        mock_common_deps["RepositoryContributor"].bulk_save.assert_called_once()
        
        assert org == mock_common_deps["Organization"].update_data.return_value
        assert repo == mock_common_deps["Repository"].update_data.return_value


    def test_owasp_site_repo_skips_languages_and_releases(
        self, mock_common_deps, mock_gh_repository
    ):
        """Tests that OWASP site repos skip fetching languages and releases."""

        mock_common_deps["check_owasp"].return_value = True

        sync_repository(mock_gh_repository)

        mock_gh_repository.get_languages.assert_not_called()

        mock_common_deps["Release"].bulk_save.assert_called_once_with([])


    def test_archived_repo_skips_syncing_items(self, mock_common_deps, mock_gh_repository):
        """Tests that archived repos skip syncing milestones, issues, and PRs."""
        mock_common_deps["Repository"].update_data.return_value.is_archived = True

        sync_repository(mock_gh_repository)

        mock_gh_repository.get_milestones.assert_not_called()
        mock_gh_repository.get_issues.assert_not_called()
        mock_gh_repository.get_pulls.assert_not_called()


    def test_repo_with_issue_tracking_disabled(self, mock_common_deps, mock_gh_repository):
        """Tests that repos with issue tracking disabled skip syncing issues."""
        mock_repo = mock_common_deps["Repository"].update_data.return_value
        mock_repo.track_issues = False

        sync_repository(mock_gh_repository)

        mock_gh_repository.get_issues.assert_not_called()
        mock_common_deps["logger"].info.assert_called_with(
            "Skipping issues sync for %s", mock_repo.name
        )


    def test_sync_stops_when_item_is_older_than_until_date(
        self, mock_common_deps, mock_gh_repository
    ):
        """Tests that syncing stops for items older than the 'until' date."""
        now = timezone.now()
        mock_repo = mock_common_deps["Repository"].update_data.return_value
        mock_repo.latest_updated_issue = MagicMock(updated_at=now - td(days=10))

        gh_issue_new = MagicMock(
            updated_at=now - td(days=1), pull_request=None, milestone=None
        )
        gh_issue_old = MagicMock(updated_at=now - td(days=20), pull_request=None)
        mock_gh_repository.get_issues.return_value = [gh_issue_new, gh_issue_old]

        sync_repository(mock_gh_repository)

        assert mock_common_deps["Issue"].update_data.call_count == 1
        mock_common_deps["Issue"].update_data.assert_called_once_with(
            gh_issue_new,
            author=mock_common_deps["User"].update_data.return_value,
            milestone=None,
            repository=mock_repo,
        )



    def test_label_sync_handles_unknownobjectexception(
        self, mock_common_deps, mock_gh_repository
    ):
        """Tests that UnknownObjectException is caught during label sync."""
        gh_issue = MagicMock(updated_at=timezone.now(), pull_request=None)
        gh_issue.labels = [MagicMock()]
        mock_gh_repository.get_issues.return_value = [gh_issue]

        mock_common_deps["Label"].update_data.side_effect = UnknownObjectException(
            status=404, data={}, headers={}
        )
        issue_url_mock = MagicMock()
        mock_common_deps["Issue"].update_data.return_value.url=issue_url_mock

        sync_repository(mock_gh_repository)

        mock_common_deps["logger"].exception.assert_called_once_with("Couldn't get GitHub issue label %s", issue_url_mock)
        assert "Couldn't get GitHub issue label" in mock_common_deps["logger"].exception.call_args[0][0]



    def test_contributor_sync_skips_if_user_update_fails(
        self, mock_common_deps, mock_gh_repository
    ):
        """Tests that a contributor is skipped if User.update_data returns None."""
        gh_contributor = MagicMock(name="gh_contributor")
        mock_gh_repository.get_contributors.return_value = [gh_contributor]
        mock_common_deps["RepositoryContributor"].update_data.side_effect = lambda gh_contributor, **kwargs: gh_contributor
        mock_common_deps["User"].update_data.side_effect = [gh_contributor, gh_contributor, None]

        sync_repository(mock_gh_repository)

        mock_common_deps["RepositoryContributor"].bulk_save.assert_called_once_with([gh_contributor])



    def test_no_organization_on_gh_repository(self, mock_common_deps, mock_gh_repository):
        """Tests that sync works correctly when the repo has no organization."""
        mock_gh_repository.organization = None

        sync_repository(mock_gh_repository)

        mock_common_deps["Organization"].update_data.assert_not_called()
        mock_common_deps["User"].update_data.assert_called_once()
        mock_common_deps["Repository"].update_data.assert_called_once()



    def test_not_archived_and_owasp_site_repo(self, mock_common_deps, mock_gh_repository):
        """Tests an OWASP site repo that is not archived proceeds with item sync."""
        mock_common_deps["check_owasp"].return_value = True
        mock_common_deps["Repository"].update_data.return_value.is_archived = False

        sync_repository(mock_gh_repository)

        mock_gh_repository.get_languages.assert_not_called()

        mock_gh_repository.get_milestones.assert_called_once()
        mock_gh_repository.get_issues.assert_called_once()
        mock_gh_repository.get_pulls.assert_called_once()



    def test_release_bulk_save_with_new_release(self, mock_common_deps, mock_gh_repository):
        """Tests that Release.bulk_save receives the expected list when a new release is found."""
        # Arrange
        mock_common_deps["check_owasp"].return_value = False  # Ensure releases are processed
        mock_common_deps["Release"].objects.filter.return_value.values_list.return_value = set()

        gh_release = MagicMock(name="gh_release")
        gh_release.node_id = "new_release_node_id"
        mock_gh_repository.get_releases.return_value = [gh_release]

        mock_updated_release = mock_common_deps["Release"].update_data.return_value


        sync_repository(mock_gh_repository)

        mock_common_deps["Release"].update_data.assert_called_once_with(
            gh_release,
            author=mock_common_deps["User"].update_data.return_value,
            repository=mock_common_deps["Repository"].update_data.return_value,
        )
        mock_common_deps["Release"].bulk_save.assert_called_once_with([mock_updated_release])



    def test_initial_sync_uses_30_day_fallback(self, mock_common_deps, mock_gh_repository):
        """Tests that the 30-day fallback is used for initial sync."""
        now = timezone.now()
        mock_repo = mock_common_deps["Repository"].update_data.return_value
        mock_repo.latest_updated_issue = None

        gh_issue_recent = MagicMock(
            updated_at=now - td(days=25), pull_request=None, milestone=None
        )
        gh_issue_ancient = MagicMock(
            updated_at=now - td(days=35), pull_request=None, milestone=None
        )
        mock_gh_repository.get_issues.return_value = [gh_issue_recent, gh_issue_ancient]

        sync_repository(mock_gh_repository)

        assert mock_common_deps["Issue"].update_data.call_count == 1
        mock_common_deps["Issue"].update_data.assert_called_once_with(
            gh_issue_recent,
            author=mock_common_deps["User"].update_data.return_value,
            milestone=None,
            repository=mock_repo,
        )