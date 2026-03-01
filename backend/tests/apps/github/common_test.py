from datetime import timedelta as td
from unittest.mock import MagicMock

import pytest
from django.utils import timezone
from github.GithubException import UnknownObjectException

from apps.github.common import sync_issue_comments, sync_repository


@pytest.fixture
def mock_common_deps(mocker):
    """Mock all dependencies for the sync_repository function."""
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

    return mocks


@pytest.fixture
def mock_gh_repository():
    """Provide a mock GitHub repository object from the pygithub library."""
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


@pytest.fixture
def mock_repo(mock_common_deps):
    """Provide the mock repository instance returned by Repository.update_data."""
    return mock_common_deps["Repository"].update_data.return_value


@pytest.fixture
def gh_item_factory():
    """Create a factory to create mock GitHub items (issues, PRs, milestones)."""

    def _create_item(**kwargs):
        item = MagicMock()
        item.updated_at = kwargs.pop("updated_at", timezone.now())
        item.pull_request = kwargs.pop("pull_request", None)
        item.milestone = kwargs.pop("milestone", None)
        item.assignees = kwargs.pop("assignees", [])
        item.labels = kwargs.pop("labels", [])
        item.creator = kwargs.pop("creator", MagicMock())
        item.get_labels = lambda: item.labels
        for key, value in kwargs.items():
            setattr(item, key, value)

        return item

    return _create_item


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

    def test_archived_repo_skips_syncing_items(self, mock_repo, mock_gh_repository):
        """Tests that archived repos skip syncing milestones, issues, and PRs."""
        mock_repo.is_archived = True
        sync_repository(mock_gh_repository)
        mock_gh_repository.get_milestones.assert_not_called()
        mock_gh_repository.get_issues.assert_not_called()
        mock_gh_repository.get_pulls.assert_not_called()

    def test_repo_with_issue_tracking_disabled(
        self, mock_common_deps, mock_gh_repository, mock_repo
    ):
        """Tests that repos with issue tracking disabled skip syncing issues."""
        mock_repo.track_issues = False
        sync_repository(mock_gh_repository)
        mock_gh_repository.get_issues.assert_not_called()
        mock_common_deps["logger"].info.assert_called_with(
            "Skipping issues sync for %s", mock_repo.name
        )

    def test_sync_stops_when_item_is_older_than_until_date(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Tests that syncing stops for items older than the 'until' date."""
        now = timezone.now()
        mock_repo.latest_updated_issue = MagicMock(updated_at=now - td(days=10))
        gh_issue_new = gh_item_factory(updated_at=now - td(days=1))
        gh_issue_old = gh_item_factory(updated_at=now - td(days=20))
        mock_gh_repository.get_issues.return_value = [gh_issue_new, gh_issue_old]

        sync_repository(mock_gh_repository)

        mock_common_deps["Issue"].update_data.assert_called_once_with(
            gh_issue_new,
            author=mock_common_deps["User"].update_data.return_value,
            milestone=None,
            repository=mock_repo,
        )

    def test_label_sync_handles_unknownobjectexception(
        self, mock_common_deps, mock_gh_repository, gh_item_factory
    ):
        """Tests that UnknownObjectException is caught during label sync."""
        gh_issue = gh_item_factory(labels=[MagicMock()])
        mock_gh_repository.get_issues.return_value = [gh_issue]
        mock_common_deps["Label"].update_data.side_effect = UnknownObjectException(
            status=404, data={}, headers={}
        )
        issue_url_mock = mock_common_deps["Issue"].update_data.return_value.url

        sync_repository(mock_gh_repository)

        mock_common_deps["logger"].exception.assert_called_once_with(
            "Couldn't get GitHub issue label %s", issue_url_mock
        )

    def test_contributor_sync_skips_if_user_update_fails(
        self, mock_common_deps, mock_gh_repository
    ):
        """Tests that a contributor is skipped if User.update_data returns None."""
        gh_valid = MagicMock(name="gh_contributor_valid")
        gh_invalid = MagicMock(name="gh_contributor_invalid")
        mock_gh_repository.get_contributors.return_value = [gh_valid, gh_invalid]
        mock_common_deps["RepositoryContributor"].update_data.side_effect = (
            lambda gh_contributor, **kwargs: gh_contributor  # noqa: ARG005
        )
        owner_user = MagicMock(name="owner_user")
        valid_user = MagicMock(name="valid_user")
        mock_common_deps["User"].update_data.side_effect = [
            owner_user,
            valid_user,
            None,
        ]

        sync_repository(mock_gh_repository)

        mock_common_deps["RepositoryContributor"].update_data.assert_called_once_with(
            gh_valid,
            repository=mock_common_deps["Repository"].update_data.return_value,
            user=valid_user,
        )
        mock_common_deps["RepositoryContributor"].bulk_save.assert_called_once_with([gh_valid])

    def test_no_organization_on_gh_repository(self, mock_common_deps, mock_gh_repository):
        """Tests that sync works correctly when the repo has no organization."""
        mock_gh_repository.organization = None
        sync_repository(mock_gh_repository)
        mock_common_deps["Organization"].update_data.assert_not_called()
        mock_common_deps["User"].update_data.assert_called_once()
        mock_common_deps["Repository"].update_data.assert_called_once()

    def test_not_archived_and_owasp_site_repo(
        self, mock_common_deps, mock_gh_repository, mock_repo
    ):
        """Tests an OWASP site repo that is not archived proceeds with item sync."""
        mock_common_deps["check_owasp"].return_value = True
        mock_repo.is_archived = False
        sync_repository(mock_gh_repository)
        mock_gh_repository.get_languages.assert_not_called()
        mock_gh_repository.get_milestones.assert_called_once()
        mock_gh_repository.get_issues.assert_called_once()
        mock_gh_repository.get_pulls.assert_called_once()

    def test_release_bulk_save_with_new_release(
        self, mock_common_deps, mock_gh_repository, mock_repo
    ):
        """Tests that Release.bulk_save receives the expected list when a new release is found."""
        mock_common_deps["Release"].objects.filter.return_value.values_list.return_value = set()
        gh_release = MagicMock(name="gh_release")
        mock_gh_repository.get_releases.return_value = [gh_release]
        mock_updated_release = mock_common_deps["Release"].update_data.return_value

        sync_repository(mock_gh_repository)

        mock_common_deps["Release"].update_data.assert_called_once_with(
            gh_release,
            author=mock_common_deps["User"].update_data.return_value,
            repository=mock_repo,
        )
        mock_common_deps["Release"].bulk_save.assert_called_once_with([mock_updated_release])

    def test_initial_sync_uses_30_day_fallback(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Tests that the 30-day fallback is used for initial sync."""
        now = timezone.now()
        mock_repo.latest_updated_issue = None
        gh_issue_recent = gh_item_factory(updated_at=now - td(days=25))
        gh_issue_ancient = gh_item_factory(updated_at=now - td(days=35))
        mock_gh_repository.get_issues.return_value = [gh_issue_recent, gh_issue_ancient]

        sync_repository(mock_gh_repository)

        mock_common_deps["Issue"].update_data.assert_called_once_with(
            gh_issue_recent,
            author=mock_common_deps["User"].update_data.return_value,
            milestone=None,
            repository=mock_repo,
        )

    def test_skips_issues_that_are_pull_requests(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Ensures that items from get_issues with a pull_request attribute are skipped."""
        gh_issue_is_pr = gh_item_factory(pull_request=True)
        gh_issue_is_issue = gh_item_factory()
        mock_gh_repository.get_issues.return_value = [gh_issue_is_pr, gh_issue_is_issue]

        sync_repository(mock_gh_repository)

        mock_common_deps["Issue"].update_data.assert_called_once_with(
            gh_issue_is_issue,
            author=mock_common_deps["User"].update_data.return_value,
            milestone=None,
            repository=mock_repo,
        )

    def test_syncs_milestone_on_issue(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Tests that milestones are correctly synced when attached to an issue."""
        gh_milestone = gh_item_factory()
        gh_issue = gh_item_factory(milestone=gh_milestone)
        mock_gh_repository.get_issues.return_value = [gh_issue]

        sync_repository(mock_gh_repository)

        mock_common_deps["Milestone"].update_data.assert_called_once_with(
            gh_milestone,
            author=mock_common_deps["User"].update_data.return_value,
            repository=mock_repo,
        )
        mock_common_deps["Issue"].update_data.assert_called_once()

    def test_syncs_assignees_on_pull_request(
        self, mock_common_deps, mock_gh_repository, gh_item_factory
    ):
        """Tests that assignees are correctly synced for a pull request."""
        gh_assignee = MagicMock()
        gh_pr = gh_item_factory(assignees=[gh_assignee])
        mock_gh_repository.get_pulls.return_value = [gh_pr]
        mock_pr_instance = mock_common_deps["PullRequest"].update_data.return_value
        mock_user_instance = mock_common_deps["User"].update_data.return_value

        sync_repository(mock_gh_repository)

        mock_common_deps["User"].update_data.assert_any_call(gh_assignee)
        mock_pr_instance.assignees.add.assert_called_once_with(mock_user_instance)

    def test_milestone_sync_stops_when_older_than_until(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Tests that milestone syncing stops when an older milestone is reached."""
        recent_time = timezone.now()
        old_time = timezone.now() - td(days=60)

        gh_milestone_recent = gh_item_factory(updated_at=recent_time)
        gh_milestone_old = gh_item_factory(updated_at=old_time)
        mock_gh_repository.get_milestones.return_value = [gh_milestone_recent, gh_milestone_old]

        sync_repository(mock_gh_repository)

        assert mock_common_deps["Milestone"].update_data.call_count == 1

    def test_pull_request_sync_stops_when_older_than_until(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Tests that pull request syncing stops when an older PR is reached."""
        recent_time = timezone.now()
        old_time = timezone.now() - td(days=60)

        gh_pr_recent = gh_item_factory(updated_at=recent_time)
        gh_pr_old = gh_item_factory(updated_at=old_time)
        mock_gh_repository.get_pulls.return_value = [gh_pr_recent, gh_pr_old]

        sync_repository(mock_gh_repository)

        assert mock_common_deps["PullRequest"].update_data.call_count == 1

    def test_issue_assignee_skipped_when_user_update_returns_none(
        self, mock_common_deps, mock_gh_repository, gh_item_factory
    ):
        """Tests that issue assignees are skipped when User.update_data returns None."""
        gh_assignee_valid = MagicMock()
        gh_assignee_invalid = MagicMock()
        gh_issue = gh_item_factory(assignees=[gh_assignee_valid, gh_assignee_invalid])
        mock_gh_repository.get_issues.return_value = [gh_issue]

        mock_issue_instance = mock_common_deps["Issue"].update_data.return_value
        valid_user = MagicMock()

        mock_common_deps["User"].update_data.side_effect = [
            MagicMock(),
            MagicMock(),
            valid_user,
            None,
        ]

        sync_repository(mock_gh_repository)

        mock_issue_instance.assignees.add.assert_called_once_with(valid_user)

    def test_pull_request_assignee_skipped_when_user_update_returns_none(
        self, mock_common_deps, mock_gh_repository, gh_item_factory
    ):
        """Tests that pull request assignees are skipped when User.update_data returns None."""
        gh_assignee_valid = MagicMock()
        gh_assignee_invalid = MagicMock()
        gh_pr = gh_item_factory(assignees=[gh_assignee_valid, gh_assignee_invalid])
        mock_gh_repository.get_pulls.return_value = [gh_pr]

        mock_pr_instance = mock_common_deps["PullRequest"].update_data.return_value
        valid_user = MagicMock()

        mock_common_deps["User"].update_data.side_effect = [
            MagicMock(),
            MagicMock(),
            valid_user,
            None,
        ]

        sync_repository(mock_gh_repository)

        mock_pr_instance.assignees.add.assert_called_once_with(valid_user)

    def test_pull_request_label_sync_handles_unknownobjectexception(
        self, mock_common_deps, mock_gh_repository, gh_item_factory
    ):
        """Tests that UnknownObjectException is caught during PR label sync."""
        gh_pr = gh_item_factory(labels=[MagicMock()])
        mock_gh_repository.get_pulls.return_value = [gh_pr]
        mock_common_deps["Label"].update_data.side_effect = UnknownObjectException(
            status=404, data={}, headers={}
        )
        pr_url_mock = mock_common_deps["PullRequest"].update_data.return_value.url

        sync_repository(mock_gh_repository)

        mock_common_deps["logger"].exception.assert_called_with(
            "Couldn't get GitHub pull request label %s", pr_url_mock
        )

    def test_release_sync_stops_at_existing_release(
        self, mock_common_deps, mock_gh_repository, mock_repo
    ):
        """Tests that release syncing stops when an existing release is found."""
        existing_node_id = "existing_release_node_id"
        mock_common_deps["Release"].objects.filter.return_value.values_list.return_value = {
            existing_node_id
        }
        gh_release_new = MagicMock()
        mock_common_deps["Release"].get_node_id.side_effect = ["new_node_id", existing_node_id]
        gh_release_existing = MagicMock()
        mock_gh_repository.get_releases.return_value = [gh_release_new, gh_release_existing]

        sync_repository(mock_gh_repository)

        mock_common_deps["Release"].update_data.assert_called_once_with(
            gh_release_new,
            author=mock_common_deps["User"].update_data.return_value,
            repository=mock_repo,
        )
        assert (
            mock_common_deps["Release"].bulk_save.call_args[0][0][0]
            == mock_common_deps["Release"].update_data.return_value
        )
        assert len(mock_common_deps["Release"].bulk_save.call_args[0][0]) == 1

    def test_sync_repository_full_scenario(
        self, mock_common_deps, mock_gh_repository, mock_repo, gh_item_factory
    ):
        """Tests a complex scenario covering multiple uncovered edge cases."""
        pre_provided_org = MagicMock()
        pre_provided_user = MagicMock()
        gh_milestone = gh_item_factory(labels=[MagicMock()])
        mock_gh_repository.get_milestones.return_value = [gh_milestone]
        gh_issue = gh_item_factory(assignees=[MagicMock()])
        mock_gh_repository.get_issues.return_value = [gh_issue]
        gh_pr = gh_item_factory(milestone=gh_item_factory(), labels=[MagicMock()])
        mock_gh_repository.get_pulls.return_value = [gh_pr]
        mock_common_deps["Label"].update_data.side_effect = [
            UnknownObjectException(status=404, data={}, headers={}),
            MagicMock(),
        ]

        sync_repository(
            mock_gh_repository,
            organization=pre_provided_org,
            user=pre_provided_user,
        )

        assert not mock_common_deps["Organization"].update_data.called
        assert mock_gh_repository.owner not in [
            c[0][0] for c in mock_common_deps["User"].update_data.call_args_list
        ]
        mock_common_deps["Milestone"].update_data.assert_any_call(
            gh_milestone,
            author=mock_common_deps["User"].update_data.return_value,
            repository=mock_repo,
        )
        mock_common_deps["logger"].exception.assert_any_call(
            "Couldn't get GitHub milestone label %s",
            mock_common_deps["Milestone"].update_data.return_value.url,
        )
        mock_common_deps["Issue"].update_data.assert_called_once()
        mock_common_deps["Issue"].update_data.return_value.assignees.add.assert_called_once_with(
            mock_common_deps["User"].update_data.return_value
        )
        mock_common_deps["PullRequest"].update_data.assert_called_once()
        mock_common_deps["Milestone"].update_data.assert_any_call(
            gh_pr.milestone,
            author=mock_common_deps["User"].update_data.return_value,
            repository=mock_repo,
        )
        mock_common_deps["PullRequest"].update_data.return_value.labels.add.assert_called_once()


class TestSyncIssueComments:
    """Tests for the sync_issue_comments function."""

    @pytest.fixture
    def mock_comment_deps(self, mocker):
        """Mock all dependencies for the sync_issue_comments function."""
        return {
            "User": mocker.patch("apps.github.common.User"),
            "Comment": mocker.patch("apps.github.common.Comment"),
            "logger": mocker.patch("apps.github.common.logger"),
        }

    @pytest.fixture
    def mock_gh_client(self):
        """Provide a mock GitHub client."""
        return MagicMock()

    @pytest.fixture
    def mock_issue(self):
        """Provide a mock Issue model instance."""
        issue = MagicMock()
        issue.number = 42
        issue.repository = MagicMock()
        issue.repository.path = "owasp/test-repo"
        issue.latest_comment = None
        issue.updated_at = timezone.now() - td(days=1)
        return issue

    def test_sync_issue_comments_no_repository(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test that sync_issue_comments logs warning when issue has no repository."""
        mock_issue.repository = None

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_comment_deps["logger"].warning.assert_called_once_with(
            "Issue #%s has no repository, skipping", mock_issue.number
        )

    def test_sync_issue_comments_basic_success(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test successful comment sync."""
        mock_gh_comment = MagicMock()
        mock_gh_comment.user = MagicMock()
        mock_gh_comment.id = 123

        mock_gh_repo = MagicMock()
        mock_gh_issue = MagicMock()
        mock_gh_repo.get_issue.return_value = mock_gh_issue
        mock_gh_issue.get_comments.return_value = [mock_gh_comment]
        mock_gh_client.get_repo.return_value = mock_gh_repo

        mock_comment_deps["User"].update_data.return_value = MagicMock()
        mock_comment = MagicMock()
        mock_comment_deps["Comment"].update_data.return_value = mock_comment

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_comment_deps["User"].update_data.assert_called_with(mock_gh_comment.user)
        mock_comment_deps["Comment"].update_data.assert_called_once()
        mock_comment_deps["Comment"].bulk_save.assert_called_once_with([mock_comment])

    def test_sync_issue_comments_with_latest_comment(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test sync_issue_comments uses latest_comment time for 'since'."""
        mock_issue.latest_comment = MagicMock()
        mock_issue.latest_comment.updated_at = timezone.now() - td(days=2)
        mock_issue.latest_comment.created_at = timezone.now() - td(days=3)

        mock_gh_repo = MagicMock()
        mock_gh_issue = MagicMock()
        mock_gh_repo.get_issue.return_value = mock_gh_issue
        mock_gh_issue.get_comments.return_value = []
        mock_gh_client.get_repo.return_value = mock_gh_repo

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_gh_issue.get_comments.assert_called_once_with(
            since=mock_issue.latest_comment.updated_at
        )

    def test_sync_issue_comments_author_update_fails(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test sync_issue_comments skips comment when author update fails."""
        mock_gh_comment = MagicMock()
        mock_gh_comment.user = MagicMock()
        mock_gh_comment.id = 456

        mock_gh_repo = MagicMock()
        mock_gh_issue = MagicMock()
        mock_gh_repo.get_issue.return_value = mock_gh_issue
        mock_gh_issue.get_comments.return_value = [mock_gh_comment]
        mock_gh_client.get_repo.return_value = mock_gh_repo

        mock_comment_deps["User"].update_data.return_value = None

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_comment_deps["logger"].warning.assert_called_with(
            "Could not sync author for comment %s", mock_gh_comment.id
        )
        mock_comment_deps["Comment"].update_data.assert_not_called()
        mock_comment_deps["Comment"].bulk_save.assert_not_called()

    def test_sync_issue_comments_unknown_object_exception(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test sync_issue_comments handles UnknownObjectException."""
        mock_gh_client.get_repo.side_effect = UnknownObjectException(
            status=404, data={}, headers={}
        )

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_comment_deps["logger"].warning.assert_called()

    def test_sync_issue_comments_unexpected_exception(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test sync_issue_comments handles unexpected exceptions."""
        mock_gh_client.get_repo.side_effect = RuntimeError("Unexpected error")

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_comment_deps["logger"].exception.assert_called()

    def test_sync_issue_comments_no_since_date(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test sync_issue_comments with no since date fallback."""
        mock_issue.latest_comment = None
        mock_issue.updated_at = None

        mock_gh_repo = MagicMock()
        mock_gh_issue = MagicMock()
        mock_gh_repo.get_issue.return_value = mock_gh_issue
        mock_gh_issue.get_comments.return_value = []
        mock_gh_client.get_repo.return_value = mock_gh_repo

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_gh_issue.get_comments.assert_called_once_with()

    def test_sync_issue_comments_latest_comment_uses_created_at(
        self, mock_comment_deps, mock_gh_client, mock_issue
    ):
        """Test sync_issue_comments uses created_at when updated_at is None."""
        created_at = timezone.now() - td(days=5)
        mock_issue.latest_comment = MagicMock()
        mock_issue.latest_comment.updated_at = None
        mock_issue.latest_comment.created_at = created_at

        mock_gh_repo = MagicMock()
        mock_gh_issue = MagicMock()
        mock_gh_repo.get_issue.return_value = mock_gh_issue
        mock_gh_issue.get_comments.return_value = []
        mock_gh_client.get_repo.return_value = mock_gh_repo

        sync_issue_comments(mock_gh_client, mock_issue)

        mock_gh_issue.get_comments.assert_called_once_with(since=created_at)
