"""Tests for GitHub common module."""

import datetime
from unittest import TestCase, mock

from github.GithubException import UnknownObjectException

from apps.github.common import sync_repository
from apps.github.models.issue import Issue
from apps.github.models.label import Label
from apps.github.models.organization import Organization
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User


class MockProject:
    """Mock Project class to avoid database dependency."""

    def __init__(self, name="Test Project", track_issues=True):
        self.name = name
        self.track_issues = track_issues
        self.id = 1

    def save(self):
        """Mock save method."""


class TestSyncRepository(TestCase):
    """Test sync_repository function."""

    def setUp(self):
        """Set up test data."""
        self.project = MockProject()

        self.gh_repository = mock.MagicMock()
        self.gh_repository.name = "test-repo"
        self.gh_repository.is_archived = False
        self.gh_repository.owner = mock.MagicMock()

        self.gh_organization = mock.MagicMock()
        self.gh_organization.login = "test-org"

        self.gh_owner = mock.MagicMock()
        self.gh_owner.login = "test-user"

        self.gh_repository.organization = self.gh_organization
        self.gh_repository.owner = self.gh_owner

        self.org_update_patch = mock.patch(
            "apps.github.models.organization.Organization.update_data"
        )
        self.user_update_patch = mock.patch("apps.github.models.user.User.update_data")
        self.repo_update_patch = mock.patch("apps.github.models.repository.Repository.update_data")
        self.issue_update_patch = mock.patch("apps.github.models.issue.Issue.update_data")
        self.label_update_patch = mock.patch("apps.github.models.label.Label.update_data")
        self.release_update_patch = mock.patch("apps.github.models.release.Release.update_data")
        self.contributor_update_patch = mock.patch(
            "apps.github.models.repository_contributor.RepositoryContributor.update_data"
        )

        self.mock_org_update = self.org_update_patch.start()
        self.mock_user_update = self.user_update_patch.start()
        self.mock_repo_update = self.repo_update_patch.start()
        self.mock_issue_update = self.issue_update_patch.start()
        self.mock_label_update = self.label_update_patch.start()
        self.mock_release_update = self.release_update_patch.start()
        self.mock_contributor_update = self.contributor_update_patch.start()

        self.mock_org_obj = mock.MagicMock(spec=Organization)
        self.mock_user_obj = mock.MagicMock(spec=User)
        self.mock_repo_obj = mock.MagicMock(spec=Repository)
        self.mock_issue_obj = mock.MagicMock(spec=Issue)
        self.mock_label_obj = mock.MagicMock(spec=Label)
        self.mock_release_obj = mock.MagicMock(spec=Release)
        self.mock_contributor_obj = mock.MagicMock(spec=RepositoryContributor)

        self.mock_org_update.return_value = self.mock_org_obj
        self.mock_user_update.return_value = self.mock_user_obj
        self.mock_repo_update.return_value = self.mock_repo_obj
        self.mock_issue_update.return_value = self.mock_issue_obj
        self.mock_label_update.return_value = self.mock_label_obj
        self.mock_release_update.return_value = self.mock_release_obj
        self.mock_contributor_update.return_value = self.mock_contributor_obj

        self.mock_repo_obj.is_archived = False
        self.mock_repo_obj.track_issues = True
        self.mock_repo_obj.project = self.project
        self.mock_repo_obj.name = "test-repo"
        self.mock_repo_obj.latest_updated_issue = None
        self.mock_repo_obj.id = 1

        self.release_bulk_save_patch = mock.patch("apps.github.models.release.Release.bulk_save")
        self.mock_release_bulk_save = self.release_bulk_save_patch.start()

        self.contributor_bulk_save_patch = mock.patch(
            "apps.github.models.repository_contributor.RepositoryContributor.bulk_save"
        )
        self.mock_contributor_bulk_save = self.contributor_bulk_save_patch.start()

        self.check_owasp_patch = mock.patch("apps.github.common.check_owasp_site_repository")
        self.mock_check_owasp = self.check_owasp_patch.start()
        self.mock_check_owasp.return_value = False

        self.release_objects_filter_patch = mock.patch(
            "apps.github.models.release.Release.objects"
        )
        self.mock_release_objects_filter = self.release_objects_filter_patch.start()
        mock_filter_return = mock.MagicMock()
        mock_filter_return.values_list.return_value = []
        self.mock_release_objects_filter.filter.return_value = mock_filter_return

    def tearDown(self):
        """Clean up patches."""
        self.org_update_patch.stop()
        self.user_update_patch.stop()
        self.repo_update_patch.stop()
        self.issue_update_patch.stop()
        self.label_update_patch.stop()
        self.release_update_patch.stop()
        self.contributor_update_patch.stop()
        self.release_bulk_save_patch.stop()
        self.contributor_bulk_save_patch.stop()
        self.check_owasp_patch.stop()
        self.release_objects_filter_patch.stop()

    def test_sync_repository_basic(self):
        """Test basic repository sync."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_issues.return_value = []
        self.gh_repository.get_releases.return_value = []

        organization, repository = sync_repository(self.gh_repository)

        self.mock_org_update.assert_called_once_with(self.gh_organization)
        self.mock_user_update.assert_called_with(self.gh_owner)
        self.mock_repo_update.assert_called_once()
        self.mock_contributor_bulk_save.assert_called_once()
        self.mock_release_bulk_save.assert_called_once()

        assert organization == self.mock_org_obj
        assert repository == self.mock_repo_obj

    def test_sync_repository_with_provided_org_and_user(self):
        """Test repository sync with provided organization and user."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_issues.return_value = []
        self.gh_repository.get_releases.return_value = []

        provided_org = mock.MagicMock(spec=Organization)
        provided_user = mock.MagicMock(spec=User)

        mock_contributor = mock.MagicMock()
        self.gh_repository.get_contributors.return_value = [mock_contributor]

        organization, repository = sync_repository(
            self.gh_repository, organization=provided_org, user=provided_user
        )

        self.mock_org_update.assert_not_called()

        self.mock_user_update.assert_called_with(mock_contributor)

        assert organization == provided_org
        assert repository == self.mock_repo_obj

    def test_sync_repository_for_owasp_site(self):
        """Test repository sync for OWASP site repository."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_issues.return_value = []
        self.gh_repository.get_releases.return_value = []

        self.mock_check_owasp.return_value = True

        organization, repository = sync_repository(self.gh_repository)

        self.gh_repository.get_languages.assert_not_called()

        args, kwargs = self.mock_repo_update.call_args
        assert kwargs.get("languages") is None

        self.mock_release_bulk_save.assert_called_once_with([])

    def test_sync_repository_with_issues(self):
        """Test repository sync with issues."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}

        mock_issue1 = mock.MagicMock()
        mock_issue1.pull_request = None
        mock_issue1.user = mock.MagicMock()
        mock_issue1.assignees = [mock.MagicMock()]
        mock_issue1.labels = [mock.MagicMock()]

        mock_issue2 = mock.MagicMock()
        mock_issue2.pull_request = True

        self.gh_repository.get_issues.return_value = [mock_issue1, mock_issue2]
        self.gh_repository.get_releases.return_value = []

        self.mock_issue_obj.assignees = mock.MagicMock()
        self.mock_issue_obj.labels = mock.MagicMock()
        self.mock_issue_obj.url = "https://github.com/test-org/test-repo/issues/1"

        organization, repository = sync_repository(self.gh_repository)

        self.mock_issue_update.assert_called_once()
        self.mock_issue_obj.assignees.clear.assert_called_once()
        self.mock_issue_obj.assignees.add.assert_called_once()
        self.mock_issue_obj.labels.clear.assert_called_once()
        self.mock_issue_obj.labels.add.assert_called_once()

    def test_sync_repository_with_latest_updated_issue(self):
        """Test repository sync with latest updated issue."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_issues.return_value = []
        self.gh_repository.get_releases.return_value = []

        latest_issue = mock.MagicMock()
        latest_issue.updated_at = datetime.datetime.now(datetime.timezone.utc)
        self.mock_repo_obj.latest_updated_issue = latest_issue

        organization, repository = sync_repository(self.gh_repository)

        args, kwargs = self.gh_repository.get_issues.call_args
        assert kwargs.get("direction") == "asc"
        assert kwargs.get("sort") == "created"
        assert kwargs.get("state") == "all"
        assert kwargs.get("since") == latest_issue.updated_at

    def test_sync_repository_skip_issues_archived(self):
        """Test repository sync skips issues for archived repos."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_releases.return_value = []

        self.mock_repo_obj.is_archived = True

        organization, repository = sync_repository(self.gh_repository)

        self.gh_repository.get_issues.assert_not_called()

    def test_sync_repository_skip_issues_no_track(self):
        """Test repository sync skips issues for repos with track_issues=False."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_releases.return_value = []

        self.mock_repo_obj.track_issues = False

        organization, repository = sync_repository(self.gh_repository)

        self.gh_repository.get_issues.assert_not_called()

    def test_sync_repository_skip_issues_no_project(self):
        """Test repository sync skips issues for repos with no project."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_releases.return_value = []

        self.mock_repo_obj.project = None

        organization, repository = sync_repository(self.gh_repository)

        self.gh_repository.get_issues.assert_not_called()

    def test_sync_repository_skip_issues_project_no_track(self):
        """Test repository sync skips issues for repos with project.track_issues=False."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_releases.return_value = []

        self.project.track_issues = False

        organization, repository = sync_repository(self.gh_repository)

        self.gh_repository.get_issues.assert_not_called()

    def test_sync_repository_with_releases(self):
        """Test repository sync with releases."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_issues.return_value = []

        mock_release = mock.MagicMock()
        mock_release.author = mock.MagicMock()

        self.gh_repository.get_releases.return_value = [mock_release]

        with mock.patch("apps.github.models.release.Release.get_node_id") as mock_get_node_id:
            mock_get_node_id.return_value = "node-id-1"

            organization, repository = sync_repository(self.gh_repository)

            self.mock_release_update.assert_called_once_with(
                mock_release, author=self.mock_user_obj, repository=self.mock_repo_obj
            )
            self.mock_release_bulk_save.assert_called_once_with([self.mock_release_obj])

    def test_sync_repository_with_existing_releases(self):
        """Test repository sync with existing releases."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}
        self.gh_repository.get_issues.return_value = []

        mock_release = mock.MagicMock()
        mock_release.author = mock.MagicMock()

        self.gh_repository.get_releases.return_value = [mock_release]

        with mock.patch("apps.github.models.release.Release.get_node_id") as mock_get_node_id:
            mock_get_node_id.return_value = "node-id-1"

            mock_filter_return = mock.MagicMock()
            mock_filter_return.values_list.return_value = ["node-id-1"]
            self.mock_release_objects_filter.filter.return_value = mock_filter_return

            organization, repository = sync_repository(self.gh_repository)

            self.mock_release_update.assert_not_called()
            self.mock_release_bulk_save.assert_called_once_with([])

    def test_sync_repository_label_exception(self):
        """Test repository sync handles UnknownObjectException for labels."""
        self.gh_repository.get_commits.return_value = []
        self.gh_repository.get_contributors.return_value = []
        self.gh_repository.get_languages.return_value = {"Python": 1000}

        mock_issue = mock.MagicMock()
        mock_issue.pull_request = None
        mock_issue.user = mock.MagicMock()
        mock_issue.assignees = []
        mock_label = mock.MagicMock()
        mock_issue.labels = [mock_label]

        self.gh_repository.get_issues.return_value = [mock_issue]
        self.gh_repository.get_releases.return_value = []

        self.mock_issue_obj.assignees = mock.MagicMock()
        self.mock_issue_obj.labels = mock.MagicMock()
        self.mock_issue_obj.url = "https://github.com/test-org/test-repo/issues/1"

        self.mock_label_update.side_effect = UnknownObjectException(404, "Not Found")

        with self.assertLogs(level="INFO") as cm:
            organization, repository = sync_repository(self.gh_repository)

            assert "Couldn't get GitHub issue label" in cm.output[0]

        self.mock_issue_update.assert_called_once()
        self.mock_issue_obj.labels.clear.assert_called_once()
        self.mock_issue_obj.labels.add.assert_not_called()
