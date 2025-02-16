from unittest import mock

import pytest
from django.utils import timezone

from apps.owasp.exceptions import SnapshotProcessingError
from apps.owasp.management.commands.process_snapshots import Command
from apps.owasp.models.snapshot import Snapshot


class TestProcessSnapshots:
    def test_process_pending_snapshots_with_snapshots(self):
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
            mock.patch.object(command, "process_single_snapshot") as mock_process,
            mock.patch("apps.owasp.management.commands.process_snapshots.logger"),
        ):
            command.process_pending_snapshots()
            mock_process.assert_called_once_with(mock_snapshot)

    def test_process_pending_snapshots_error(self):
        """Test error handling in process_pending_snapshots."""
        command = Command()
        error_message = "Test error"

        # Create mock snapshot using MagicMock
        mock_snapshot = mock.MagicMock(spec=Snapshot)
        mock_snapshot.id = 1
        mock_snapshot.status = "pending"

        # Create mock queryset
        mock_queryset = mock.MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__iter__.return_value = [mock_snapshot]

        with (
            mock.patch(
                "apps.owasp.models.snapshot.Snapshot.objects.filter", return_value=mock_queryset
            ),
            mock.patch("django.db.transaction.atomic", return_value=mock.MagicMock()),
            mock.patch.object(
                command, "process_single_snapshot", side_effect=Exception(error_message)
            ),
            mock.patch("apps.owasp.management.commands.process_snapshots.logger") as mock_logger,
        ):
            command.process_pending_snapshots()

            # error handling
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
            mock.patch("apps.owasp.management.commands.process_snapshots.logger") as mock_logger,
        ):
            command.handle()
            mock_logger.info.assert_called_once_with("No pending snapshots found")

    def test_handle_error(self):
        """Test handle method error handling."""
        command = Command()
        error_message = "Test error"

        with (
            mock.patch.object(
                command, "process_pending_snapshots", side_effect=Exception(error_message)
            ),
            pytest.raises(SnapshotProcessingError) as exc_info,
        ):
            command.handle()

        assert str(exc_info.value) == f"Failed to process snapshot: {error_message}"
