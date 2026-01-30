from unittest import mock

import pytest
from django.utils import timezone

from apps.owasp.exceptions import SnapshotProcessingError
from apps.owasp.management.commands.owasp_process_snapshots import Command
from apps.owasp.models.snapshot import Snapshot


class TestProcessSnapshots:
    def test_process_snapshots_with_snapshots(self):
        """Test if pending snapshots are processed."""
        command = Command()

        # Create mock snapshot
        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.status = "pending"
        mock_snapshot.start_at = timezone.now()
        mock_snapshot.end_at = timezone.now()

        # Create mock queryset
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

        mock_chapters = mock.MagicMock()
        mock_chapters.filter.return_value = mock_chapters
        mock_chapters.count.return_value = 2

        mock_projects = mock.MagicMock()
        mock_projects.filter.return_value = mock_projects
        mock_projects.count.return_value = 3

        mock_issues = mock.MagicMock()
        mock_issues.count.return_value = 5

        mock_releases = mock.MagicMock()
        mock_releases.filter.return_value = mock_releases
        mock_releases.count.return_value = 1

        mock_users = mock.MagicMock()
        mock_users.count.return_value = 10

        with (
            mock.patch.object(command, "get_new_items") as mock_get_new_items,
            mock.patch("apps.owasp.management.commands.owasp_process_snapshots.logger"),
        ):
            mock_get_new_items.side_effect = [
                mock_chapters,
                mock_issues,
                mock_projects,
                mock_releases,
                mock_users,
            ]

            command.process_snapshot(mock_snapshot)

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
