"""Tests for OWASP ActivityEvent model."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from apps.github.models.generic_issue_model import GenericIssueModel
from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.owasp.models.activity_event import ActivityEvent


def _make_user():
    """Return a real (unsaved) User instance."""
    return User(login="testuser", name="Test User")


def _make_repository():
    """Return a real (unsaved) Repository instance with an owner set."""
    repo = Repository(name="test-repo")
    repo.owner = _make_user()
    return repo


def _make_issue(*, state=GenericIssueModel.IssueState.OPEN, closed_at=None):
    """Return a mock Issue."""
    issue = Mock()
    issue.__class__.__name__ = "Issue"
    issue.pk = 10
    issue.repository = _make_repository()
    issue.author = _make_user()
    issue.created_at = datetime(2024, 1, 1, tzinfo=UTC)
    issue.state = state
    issue.closed_at = closed_at
    return issue


def _make_pull_request(
    *, merged_at=None, state=GenericIssueModel.IssueState.OPEN, closed_at=None
):
    """Return a mock PullRequest."""
    pr = Mock()
    pr.__class__.__name__ = "PullRequest"
    pr.pk = 20
    pr.repository = _make_repository()
    pr.author = _make_user()
    pr.created_at = datetime(2024, 2, 1, tzinfo=UTC)
    pr.merged_at = merged_at
    pr.state = state
    pr.closed_at = closed_at
    return pr


def _make_release(*, published_at=datetime(2024, 3, 1, tzinfo=UTC)):
    """Return a mock Release."""
    release = Mock()
    release.__class__.__name__ = "Release"
    release.pk = 30
    release.repository = _make_repository()
    release.author = _make_user()
    release.published_at = published_at
    return release


class TestActivityEventStr:
    def test_str_returns_human_readable_format(self):
        """__str__ should include activity_type, github_user, and github_repository."""
        user = User(login="testuser", name="Test User")
        repo = _make_repository()

        event = ActivityEvent(
            activity_type=ActivityEvent.ActivityType.ISSUE_OPENED,
            github_user=user,
            github_repository=repo,
        )

        result = str(event)

        assert "issue_opened" in result
        assert "testuser" in result
        assert "test-repo" in result


class TestActivityEventBulkSave:
    def test_bulk_save_delegates_to_base(self):
        """bulk_save should call BulkSaveModel.bulk_save with the correct args."""
        events = [Mock(), Mock()]
        with patch(
            "apps.owasp.models.activity_event.BulkSaveModel.bulk_save"
        ) as mock_bulk_save:
            ActivityEvent.bulk_save(events, fields=["activity_type"])
            mock_bulk_save.assert_called_once_with(
                ActivityEvent, events, fields=["activity_type"]
            )


class TestBuildForIssue:
    def test_closed_issue_produces_opened_and_closed_events(self):
        """A closed issue should produce ISSUE_OPENED and ISSUE_CLOSED event tuples."""
        closed_at = datetime(2024, 1, 15, tzinfo=UTC)
        issue = _make_issue(
            state=GenericIssueModel.IssueState.CLOSED,
            closed_at=closed_at,
        )

        result = ActivityEvent.build_for_issue(issue)

        assert len(result) == 2
        types = [r[0] for r in result]
        assert ActivityEvent.ActivityType.ISSUE_OPENED in types
        assert ActivityEvent.ActivityType.ISSUE_CLOSED in types

        closed_event = next(r for r in result if r[0] == ActivityEvent.ActivityType.ISSUE_CLOSED)
        assert closed_event[1] == closed_at


class TestBuildForPullRequest:
    def test_open_pr_produces_only_opened_event(self):
        """An open PR should produce exactly one PR_OPENED event tuple.

        Covers the elif false branch on line 116 (merged_at=None, state=OPEN).
        """
        pr = _make_pull_request()

        result = ActivityEvent.build_for_pull_request(pr)

        assert len(result) == 1
        assert result[0][0] == ActivityEvent.ActivityType.PR_OPENED

    def test_merged_pr_produces_opened_and_merged_events(self):
        """A merged PR should produce PR_OPENED and PR_MERGED event tuples."""
        merged_at = datetime(2024, 2, 10, tzinfo=UTC)
        pr = _make_pull_request(merged_at=merged_at)

        result = ActivityEvent.build_for_pull_request(pr)

        assert len(result) == 2
        types = [r[0] for r in result]
        assert ActivityEvent.ActivityType.PR_OPENED in types
        assert ActivityEvent.ActivityType.PR_MERGED in types

        merged_event = next(r for r in result if r[0] == ActivityEvent.ActivityType.PR_MERGED)
        assert merged_event[1] == merged_at

    def test_closed_unmerged_pr_produces_opened_and_closed_events(self):
        """A closed (not merged) PR should produce PR_OPENED and PR_CLOSED event tuples."""
        closed_at = datetime(2024, 2, 20, tzinfo=UTC)
        pr = _make_pull_request(
            merged_at=None,
            state=GenericIssueModel.IssueState.CLOSED,
            closed_at=closed_at,
        )

        result = ActivityEvent.build_for_pull_request(pr)

        assert len(result) == 2
        types = [r[0] for r in result]
        assert ActivityEvent.ActivityType.PR_OPENED in types
        assert ActivityEvent.ActivityType.PR_CLOSED in types


class TestBuildForRelease:
    def test_unpublished_release_returns_empty_list(self):
        """A release with published_at=None should return []."""
        release = _make_release(published_at=None)

        result = ActivityEvent.build_for_release(release)

        assert result == []

    def test_published_release_returns_release_published_event(self):
        """A published release should return one RELEASE_PUBLISHED event tuple."""
        published_at = datetime(2024, 3, 1, tzinfo=UTC)
        release = _make_release(published_at=published_at)

        result = ActivityEvent.build_for_release(release)

        assert len(result) == 1
        activity_type, occurred_at, author = result[0]
        assert activity_type == ActivityEvent.ActivityType.RELEASE_PUBLISHED
        assert occurred_at == published_at
        assert author == release.author


class TestUpdateData:
    """Tests for ActivityEvent.update_data.

    ActivityEvent.__init__ is patched to bypass Django FK descriptor validation
    (which rejects plain Mock objects for ForeignKey fields), while still allowing
    the real handler dispatch and list-comprehension filtering logic to execute.
    """

    def test_returns_empty_list_when_no_repository(self):
        """update_data should return [] when source.repository is None."""
        source = Mock()
        source.repository = None

        result = ActivityEvent.update_data(source)

        assert result == []

    def test_raises_type_error_for_unsupported_model(self):
        """update_data should raise TypeError for unknown model types."""

        class UnsupportedModel:
            pass

        source = UnsupportedModel()
        source.repository = _make_repository()

        with pytest.raises(TypeError, match="Unsupported model type"):
            ActivityEvent.update_data(source)

    def test_update_data_for_open_issue(self):
        """update_data for an Issue should construct ActivityEvent instances."""
        issue = _make_issue()

        with (
            patch(
                "apps.owasp.models.activity_event.ContentType.objects.get_for_model",
                return_value=Mock(),
            ),
            patch.object(ActivityEvent, "__init__", return_value=None) as mock_init,
        ):
            result = ActivityEvent.update_data(issue)

        assert len(result) == 1
        assert mock_init.call_count == 1
        _, kwargs = mock_init.call_args
        assert kwargs["activity_type"] == ActivityEvent.ActivityType.ISSUE_OPENED
        assert kwargs["occurred_at"] == issue.created_at
        assert kwargs["object_id"] == issue.pk

    def test_update_data_for_release(self):
        """update_data for a published Release should construct one RELEASE_PUBLISHED event."""
        release = _make_release()

        with (
            patch(
                "apps.owasp.models.activity_event.ContentType.objects.get_for_model",
                return_value=Mock(),
            ),
            patch.object(ActivityEvent, "__init__", return_value=None) as mock_init,
        ):
            result = ActivityEvent.update_data(release)

        assert len(result) == 1
        assert mock_init.call_count == 1
        assert (
            mock_init.call_args_list[0][1]["activity_type"]
            == ActivityEvent.ActivityType.RELEASE_PUBLISHED
        )

    def test_update_data_filters_out_none_occurred_at(self):
        """Events with occurred_at=None should be excluded from the output list."""
        issue = _make_issue()
        issue.created_at = None

        with (
            patch(
                "apps.owasp.models.activity_event.ContentType.objects.get_for_model",
                return_value=Mock(),
            ),
            patch.object(ActivityEvent, "__init__", return_value=None),
        ):
            result = ActivityEvent.update_data(issue)

        assert result == []


class TestBulkSaveForSources:
    def test_empty_sources_list_does_not_call_bulk_create(self):
        """bulk_save_for_sources with an empty list should not call bulk_create."""
        with patch.object(ActivityEvent.objects, "bulk_create") as mock_bulk_create:
            ActivityEvent.bulk_save_for_sources([])
            mock_bulk_create.assert_not_called()

    def test_sources_with_no_events_does_not_call_bulk_create(self):
        """Sources that produce no events should not call bulk_create."""
        release = _make_release(published_at=None)

        with (
            patch.object(ActivityEvent, "update_data", return_value=[]),
            patch.object(ActivityEvent.objects, "bulk_create") as mock_bulk_create,
        ):
            ActivityEvent.bulk_save_for_sources([release])

        mock_bulk_create.assert_not_called()

    def test_sources_with_events_calls_bulk_create(self):
        """bulk_save_for_sources with valid sources should call bulk_create with ignore_conflicts."""
        issue = _make_issue()
        mock_event = Mock(spec=ActivityEvent)

        with (
            patch.object(ActivityEvent, "update_data", return_value=[mock_event]),
            patch.object(ActivityEvent.objects, "bulk_create") as mock_bulk_create,
        ):
            ActivityEvent.bulk_save_for_sources([issue])

        mock_bulk_create.assert_called_once()
        _, kwargs = mock_bulk_create.call_args
        assert kwargs.get("ignore_conflicts") is True
