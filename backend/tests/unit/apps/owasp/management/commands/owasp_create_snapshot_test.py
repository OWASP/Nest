from datetime import UTC, datetime
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_create_snapshot import Command
from apps.owasp.models.snapshot import Snapshot


class TestCreateSnapshot:
    """Tests for owasp_create_snapshot management command."""

    def test_handle_creates_snapshot_weekly(self):
        """Test that handle creates a weekly snapshot successfully."""
        command = Command()
        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.key = "2026-W24"

        with (
            mock.patch.object(
                command,
                "calculate_date_range",
                return_value=(
                    datetime(2026, 6, 8, tzinfo=UTC),
                    datetime(2026, 6, 14, 23, 59, 59, tzinfo=UTC),
                ),
            ),
            mock.patch.object(command, "generate_key", return_value="2026-W24"),
            mock.patch.object(
                command, "generate_title", return_value="Week 24 2026 OWASP Community Snapshot"
            ),
            mock.patch("apps.owasp.models.snapshot.Snapshot.objects") as mock_objects,
        ):
            mock_objects.filter.return_value.exists.return_value = False
            mock_objects.create.return_value = mock_snapshot

            command.handle(frequency="weekly")

            mock_objects.create.assert_called_once_with(
                key="2026-W24",
                start_at=datetime(2026, 6, 8, tzinfo=UTC),
                end_at=datetime(2026, 6, 14, 23, 59, 59, tzinfo=UTC),
                title="Week 24 2026 OWASP Community Snapshot",
                status=Snapshot.Status.PENDING,
            )

    def test_handle_creates_snapshot_monthly(self):
        """Test that handle creates a monthly snapshot successfully."""
        command = Command()
        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.key = "2026-05"

        with (
            mock.patch.object(
                command,
                "calculate_date_range",
                return_value=(
                    datetime(2026, 5, 1, tzinfo=UTC),
                    datetime(2026, 5, 31, 23, 59, 59, tzinfo=UTC),
                ),
            ),
            mock.patch.object(command, "generate_key", return_value="2026-05"),
            mock.patch.object(
                command, "generate_title", return_value="May 2026 OWASP Community Snapshot"
            ),
            mock.patch("apps.owasp.models.snapshot.Snapshot.objects") as mock_objects,
        ):
            mock_objects.filter.return_value.exists.return_value = False
            mock_objects.create.return_value = mock_snapshot

            command.handle(frequency="monthly")

            mock_objects.create.assert_called_once_with(
                key="2026-05",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 31, 23, 59, 59, tzinfo=UTC),
                title="May 2026 OWASP Community Snapshot",
                status=Snapshot.Status.PENDING,
            )

    def test_handle_skips_duplicate_snapshot(self):
        """Test that handle skips creation when a snapshot with the same key exists."""
        command = Command()

        with (
            mock.patch.object(
                command,
                "calculate_date_range",
                return_value=(
                    datetime(2026, 6, 8, tzinfo=UTC),
                    datetime(2026, 6, 14, 23, 59, 59, tzinfo=UTC),
                ),
            ),
            mock.patch.object(command, "generate_key", return_value="2026-W24"),
            mock.patch("apps.owasp.models.snapshot.Snapshot.objects") as mock_objects,
            mock.patch(
                "apps.owasp.management.commands.owasp_create_snapshot.logger"
            ) as mock_logger,
        ):
            mock_objects.filter.return_value.exists.return_value = True

            command.handle(frequency="weekly")

            mock_objects.create.assert_not_called()
            mock_logger.info.assert_any_call(
                "Snapshot with key '%s' already exists, skipping", "2026-W24"
            )

    @pytest.mark.parametrize(
        ("frozen_now", "expected_start", "expected_end"),
        [
            pytest.param(
                datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                datetime(2026, 6, 8, 0, 0, 0, tzinfo=UTC),
                datetime(2026, 6, 14, 23, 59, 59, tzinfo=UTC),
                id="monday-calculates-last-week",
            ),
            pytest.param(
                datetime(2026, 6, 11, 12, 0, 0, tzinfo=UTC),
                datetime(2026, 6, 1, 0, 0, 0, tzinfo=UTC),
                datetime(2026, 6, 7, 23, 59, 59, tzinfo=UTC),
                id="thursday-calculates-last-week",
            ),
        ],
    )
    def test_calculate_date_range_weekly(self, frozen_now, expected_start, expected_end):
        """Test weekly date range calculation."""
        with mock.patch(
            "apps.owasp.management.commands.owasp_create_snapshot.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = frozen_now
            mock_datetime.side_effect = datetime
            start_at, end_at = Command.calculate_date_range("weekly")

        assert start_at == expected_start
        assert end_at == expected_end

    def test_calculate_date_range_monthly(self):
        """Test monthly date range calculation."""
        frozen_now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC)

        with mock.patch(
            "apps.owasp.management.commands.owasp_create_snapshot.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = frozen_now
            mock_datetime.side_effect = datetime
            start_at, end_at = Command.calculate_date_range("monthly")

        assert start_at == datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)
        assert end_at == datetime(2026, 5, 31, 23, 59, 59, tzinfo=UTC)

    def test_generate_key_weekly(self):
        """Test key generation for weekly snapshots."""
        start_at = datetime(2026, 6, 8, tzinfo=UTC)
        key = Command.generate_key(start_at, "weekly")
        assert key == "2026-W24"

    def test_generate_key_monthly(self):
        """Test key generation for monthly snapshots."""
        start_at = datetime(2026, 5, 1, tzinfo=UTC)
        key = Command.generate_key(start_at, "monthly")
        assert key == "2026-05"

    def test_generate_title_weekly(self):
        """Test title generation for weekly snapshots."""
        start_at = datetime(2026, 6, 8, tzinfo=UTC)
        title = Command.generate_title(start_at, "weekly")
        assert title == "Week 24 2026 OWASP Community Snapshot"

    def test_generate_title_monthly(self):
        """Test title generation for monthly snapshots."""
        start_at = datetime(2026, 5, 1, tzinfo=UTC)
        title = Command.generate_title(start_at, "monthly")
        assert title == "May 2026 OWASP Community Snapshot"

    def test_generate_key_matches_model_save_weekly(self):
        """Test that generate_key produces the same key as the model's save method."""
        start_at = datetime(2026, 1, 5, tzinfo=UTC)
        key = Command.generate_key(start_at, "weekly")
        iso_year, iso_week, _ = start_at.isocalendar()
        expected = f"{iso_year}-W{iso_week:02d}"
        assert key == expected

    def test_generate_key_matches_model_save_monthly(self):
        """Test that generate_key produces the same key as the model's save method."""
        start_at = datetime(2026, 12, 1, tzinfo=UTC)
        key = Command.generate_key(start_at, "monthly")
        assert key == "2026-12"
