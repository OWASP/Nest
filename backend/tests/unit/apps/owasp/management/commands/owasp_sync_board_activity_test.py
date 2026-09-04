"""Tests for the owasp_sync_board_activity management command."""

from unittest.mock import Mock

import pytest
from django.core.management.base import CommandError

from apps.owasp.management.commands.owasp_sync_board_activity import Command
from apps.owasp.parsers.board_activity.sync import SyncStats, SyncStatus


class TestSyncBoardActivityCommand:
    """Test cases for the owasp_sync_board_activity command."""

    @pytest.fixture
    def command(self):
        """Instantiate the command with mocked I/O."""
        cmd = Command()
        cmd.stdout = Mock()
        cmd.stderr = Mock()
        cmd.style = Mock(SUCCESS=lambda s: s)
        return cmd

    def test_month_without_year_raises(self, command):
        """Passing --month without --year is rejected with a CommandError."""
        with pytest.raises(CommandError, match="--month requires --year"):
            command.handle(year=None, month=8)

    @pytest.mark.parametrize("month", [0, -1, 13, 100])
    def test_month_out_of_range_raises(self, command, month):
        """Passing --month outside 1-12 is rejected with a CommandError."""
        with pytest.raises(CommandError, match="--month must be between 1 and 12"):
            command.handle(year=2025, month=month)

    @pytest.mark.parametrize("year", [1, 202, 10000])
    def test_year_out_of_range_raises(self, command, year):
        """Passing a non-4-digit --year is rejected with a CommandError."""
        with pytest.raises(CommandError, match="4-digit"):
            command.handle(year=year, month=None)

    def test_errored_count_raises_command_error(self, command, mocker):
        """A non-zero ERRORED count exits the command with a CommandError."""
        stats = SyncStats()
        stats.record(SyncStatus.ERRORED)
        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_activity.sync.run",
            return_value=stats,
        )

        with pytest.raises(CommandError, match="errored"):
            command.handle(year=None, month=None, path=None, force=False, dry_run=False)

    def test_handle_delegates_to_sync_run(self, command, mocker):
        """CLI options are threaded through to sync.run."""
        mock_run = mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_activity.sync.run",
            return_value=SyncStats(),
        )

        command.handle(
            year=2025,
            month=8,
            path=None,
            force=True,
            dry_run=False,
        )

        mock_run.assert_called_once_with(
            year=2025,
            month=8,
            path=None,
            force=True,
            dry_run=False,
        )

    def test_summary_line_is_written(self, command, mocker):
        """The stdout summary reflects the SyncStats.counts contents."""
        stats = SyncStats()
        stats.record("created")
        stats.record("created")
        stats.record("unchanged")
        mocker.patch(
            "apps.owasp.management.commands.owasp_sync_board_activity.sync.run",
            return_value=stats,
        )

        command.handle(year=None, month=None, path=None, force=False, dry_run=False)

        written = command.stdout.write.call_args.args[0]
        assert "created=2" in written
        assert "unchanged=1" in written
