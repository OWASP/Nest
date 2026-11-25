from unittest import mock

import pytest
from django.utils import timezone

from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.exceptions import SnapshotProcessingError
from apps.owasp.management.commands.owasp_process_snapshots import Command
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.event import Event
from apps.owasp.models.post import Post
from apps.owasp.models.project import Project
from apps.owasp.models.snapshot import Snapshot


class TestProcessSnapshots:
    def test_process_snapshots_with_snapshots(self):
        """Test if pending snapshots are processed."""
        command = Command()
        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.status = "pending"
        mock_snapshot.start_at = timezone.now()
        mock_snapshot.end_at = timezone.now()
        mock_queryset = mock.MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_snapshot]

        with (
            mock.patch(
                "apps.owasp.models.snapshot.Snapshot.objects.filter", return_value=mock_queryset
            ),
            mock.patch("django.db.transaction.atomic", return_value=mock.MagicMock()),
            mock.patch.object(command, "process_snapshot") as mock_process,
            mock.patch("apps.owasp.management.commands.owasp_process_snapshots.logger"),
        ):
            command.process_snapshots()
            mock_process.assert_called_once_with(mock_snapshot)

    def test_process_snapshots_error(self):
        """Test error handling in process_snapshots."""
        command = Command()
        error_message = "Test error"

        mock_snapshot = mock.MagicMock(spec=Snapshot)
        mock_snapshot.id = 1
        mock_snapshot.status = "pending"

        mock_queryset = mock.MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_snapshot]

        with (
            mock.patch(
                "apps.owasp.models.snapshot.Snapshot.objects.filter", return_value=mock_queryset
            ),
            mock.patch("django.db.transaction.atomic", return_value=mock.MagicMock()),
            mock.patch.object(command, "process_snapshot", side_effect=Exception(error_message)),
            mock.patch(
                "apps.owasp.management.commands.owasp_process_snapshots.logger"
            ) as mock_logger,
        ):
            command.process_snapshots()

            assert mock_snapshot.status == "error"
            assert mock_snapshot.error_message == f"Error processing snapshot 1: {error_message}"
            mock_logger.exception.assert_called_once_with(
                f"Error processing snapshot {mock_snapshot.id}: {error_message}"
            )
            mock_snapshot.save.assert_called_once()

    def test_handle_no_pending_snapshots(self):
        """Test handling when no pending snapshots exist."""
        command = Command()

        mock_queryset = mock.MagicMock()
        mock_queryset.exists.return_value = False

        with (
            mock.patch(
                "apps.owasp.models.snapshot.Snapshot.objects.filter", return_value=mock_queryset
            ),
            mock.patch(
                "apps.owasp.management.commands.owasp_process_snapshots.logger"
            ) as mock_logger,
        ):
            command.handle()
            mock_logger.info.assert_called_once_with("No pending snapshots found")

    def test_handle_error(self):
        """Test handle method error handling."""
        command = Command()
        error_message = "Test error"

        with (
            mock.patch.object(command, "process_snapshots", side_effect=Exception(error_message)),
            pytest.raises(SnapshotProcessingError) as exc_info,
        ):
            command.handle()

        assert str(exc_info.value) == f"Failed to process snapshot: {error_message}"

    def test_process_snapshot_success(self):
        """Test process_snapshot successfully processes a snapshot."""
        command = Command()

        mock_snapshot = mock.MagicMock(spec=Snapshot)
        mock_snapshot.id = 1
        mock_snapshot.start_at = timezone.now()
        mock_snapshot.end_at = timezone.now()

        def make_queryset(count):
            queryset = mock.MagicMock()
            queryset.filter.return_value = queryset
            queryset.count.return_value = count
            queryset.__iter__.return_value = [mock.MagicMock() for _ in range(count)]
            return queryset

        mock_chapters = make_queryset(2)
        mock_events = make_queryset(1)
        mock_issues = make_queryset(5)
        mock_posts = make_queryset(3)
        mock_projects = make_queryset(3)
        mock_pull_requests = make_queryset(4)
        mock_releases = make_queryset(1)
        mock_users = make_queryset(10)

        with (
            mock.patch.object(command, "get_new_items") as mock_get_new_items,
            mock.patch("apps.owasp.management.commands.owasp_process_snapshots.logger"),
        ):
            mock_get_new_items.side_effect = [
                mock_chapters,
                mock_events,
                mock_issues,
                mock_posts,
                mock_projects,
                mock_pull_requests,
                mock_releases,
                mock_users,
            ]

            command.process_snapshot(mock_snapshot)

            assert mock_get_new_items.call_count == 8
            assert [call.args for call in mock_get_new_items.call_args_list] == [
                (model, mock_snapshot.start_at, mock_snapshot.end_at)
                for model in (
                    Chapter,
                    Event,
                    Issue,
                    Post,
                    Project,
                    PullRequest,
                    Release,
                    User,
                )
            ]
            assert [call.kwargs for call in mock_get_new_items.call_args_list] == [
                {},
                {"date_field": "start_date"},
                {},
                {"date_field": "published_at"},
                {},
                {},
                {},
                {},
            ]
            mock_chapters.filter.assert_called_once_with(is_active=True)
            mock_projects.filter.assert_called_once_with(is_active=True)
            mock_releases.filter.assert_called_once_with(is_draft=False, is_pre_release=False)

            for relation, queryset in (
                (mock_snapshot.chapters, mock_chapters),
                (mock_snapshot.events, mock_events),
                (mock_snapshot.issues, mock_issues),
                (mock_snapshot.posts, mock_posts),
                (mock_snapshot.projects, mock_projects),
                (mock_snapshot.pull_requests, mock_pull_requests),
                (mock_snapshot.releases, mock_releases),
                (mock_snapshot.users, mock_users),
            ):
                relation.add.assert_called_once_with(*queryset.__iter__.return_value)

            assert mock_snapshot.status == Snapshot.Status.COMPLETED
            mock_snapshot.save.assert_called()

    def test_process_snapshot_exception(self):
        """Test process_snapshot raises SnapshotProcessingError on exception."""
        command = Command()

        mock_snapshot = mock.MagicMock(spec=Snapshot)
        mock_snapshot.id = 1
        mock_snapshot.start_at = timezone.now()
        mock_snapshot.end_at = timezone.now()

        with (
            mock.patch.object(command, "get_new_items", side_effect=Exception("Database error")),
            mock.patch("apps.owasp.management.commands.owasp_process_snapshots.logger"),
            pytest.raises(SnapshotProcessingError) as exc_info,
        ):
            command.process_snapshot(mock_snapshot)

        assert "Failed to process snapshot" in str(exc_info.value)

    def test_get_new_items(self):
        """Test get_new_items filters by date range."""
        command = Command()
        start_at = timezone.now()
        end_at = timezone.now()

        mock_model = mock.MagicMock()
        mock_queryset = mock.MagicMock()
        mock_model.objects.filter.return_value = mock_queryset

        result = command.get_new_items(mock_model, start_at, end_at)

        assert result == mock_queryset
        mock_model.objects.filter.assert_called_once_with(
            created_at__gte=start_at, created_at__lte=end_at
        )

    def test_get_new_items_custom_date_field(self):
        """Test get_new_items with custom date field."""
        command = Command()
        start_at = timezone.now()
        end_at = timezone.now()

        mock_model = mock.MagicMock()
        mock_queryset = mock.MagicMock()
        mock_model.objects.filter.return_value = mock_queryset

        result = command.get_new_items(mock_model, start_at, end_at, date_field="start_date")

        assert result == mock_queryset
        mock_model.objects.filter.assert_called_once_with(
            start_date__gte=start_at, start_date__lte=end_at
        )
