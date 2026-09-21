"""Tests for SnapshotQuery."""

from datetime import datetime
from unittest.mock import MagicMock, call, patch

from apps.owasp.api.internal.queries.snapshot import SnapshotQuery, _filtered_snapshots
from apps.owasp.models.snapshot import Snapshot


class TestSnapshotQuery:
    """Test cases for SnapshotQuery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.query = SnapshotQuery()

    def test_snapshot_query_has_strawberry_definition(self):
        """Check if SnapshotQuery has valid Strawberry definition."""
        assert hasattr(SnapshotQuery, "__strawberry_definition__")

        field_names = [field.name for field in SnapshotQuery.__strawberry_definition__.fields]
        assert "snapshot" in field_names
        assert "snapshots" in field_names
        assert "snapshots_count" in field_names

    def test_snapshot_exists(self):
        """Test snapshot returns snapshot when found."""
        mock_snapshot = MagicMock(spec=Snapshot)

        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_annotate = mock_filter.return_value.annotate.return_value
            mock_annotate.get.return_value = mock_snapshot

            result = self.query.__class__.__dict__["snapshot"](self.query, key="test-key")

            assert result == mock_snapshot
            mock_filter.assert_called_once_with(
                key="test-key",
                status=Snapshot.Status.COMPLETED,
            )

    def test_snapshot_not_exists(self):
        """Test snapshot returns None when not found."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_annotate = mock_filter.return_value.annotate.return_value
            mock_annotate.get.side_effect = Snapshot.DoesNotExist

            result = self.query.__class__.__dict__["snapshot"](self.query, key="nonexistent")

            assert result is None

    def test_snapshots_with_positive_limit(self):
        """Test snapshots returns list with positive limit."""
        mock_snapshots = [MagicMock(spec=Snapshot), MagicMock(spec=Snapshot)]

        with patch(
            "apps.owasp.api.internal.queries.snapshot._filtered_snapshots"
        ) as mock_filtered:
            mock_filtered.return_value.__getitem__ = MagicMock(return_value=mock_snapshots)

            result = self.query.__class__.__dict__["snapshots"](self.query, limit=5)

            assert result == mock_snapshots

    def test_snapshots_with_zero_limit_returns_empty(self):
        """Test snapshots returns empty list when limit is 0."""
        result = self.query.__class__.__dict__["snapshots"](self.query, limit=0)

        assert result == []

    def test_snapshots_with_negative_limit_returns_empty(self):
        """Test snapshots returns empty list when limit is negative."""
        result = self.query.__class__.__dict__["snapshots"](self.query, limit=-10)

        assert result == []

    def test_snapshots_limit_clamped_to_max(self):
        """Test snapshots clamps limit to MAX_LIMIT."""
        mock_snapshots = [MagicMock(spec=Snapshot)]

        with patch(
            "apps.owasp.api.internal.queries.snapshot._filtered_snapshots"
        ) as mock_filtered:
            mock_qs = MagicMock()
            mock_qs.__getitem__ = MagicMock(return_value=mock_snapshots)
            mock_filtered.return_value = mock_qs

            result = self.query.__class__.__dict__["snapshots"](self.query, limit=500)
            assert result == mock_snapshots
            mock_qs.__getitem__.assert_called_once_with(slice(0, 100))

    def test_snapshots_with_offset(self):
        """Test snapshots uses offset for pagination."""
        mock_snapshots = [MagicMock(spec=Snapshot)]

        with patch(
            "apps.owasp.api.internal.queries.snapshot._filtered_snapshots"
        ) as mock_filtered:
            mock_qs = MagicMock()
            mock_qs.__getitem__ = MagicMock(return_value=mock_snapshots)
            mock_filtered.return_value = mock_qs

            result = self.query.__class__.__dict__["snapshots"](self.query, limit=12, offset=12)

            assert result == mock_snapshots
            mock_qs.__getitem__.assert_called_once_with(slice(12, 24))

    def test_snapshots_with_date_filters(self):
        """Test snapshots passes date filters to _filtered_snapshots."""
        mock_snapshots = [MagicMock(spec=Snapshot)]

        with patch(
            "apps.owasp.api.internal.queries.snapshot._filtered_snapshots"
        ) as mock_filtered:
            mock_filtered.return_value.__getitem__ = MagicMock(return_value=mock_snapshots)

            self.query.__class__.__dict__["snapshots"](
                self.query,
                limit=12,
                start_at_gte="2025-01-01T00:00:00",
                start_at_lte="2025-12-31T23:59:59",
            )

            mock_filtered.assert_called_once_with("2025-01-01T00:00:00", "2025-12-31T23:59:59")

    def test_snapshots_count_returns_count(self):
        """Test snapshots_count returns total count."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot._filtered_snapshots"
        ) as mock_filtered:
            mock_filtered.return_value.count.return_value = 42

            result = self.query.__class__.__dict__["snapshots_count"](self.query)

            assert result == 42

    def test_snapshots_count_with_date_filters(self):
        """Test snapshots_count passes date filters."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot._filtered_snapshots"
        ) as mock_filtered:
            mock_filtered.return_value.count.return_value = 10

            result = self.query.__class__.__dict__["snapshots_count"](
                self.query,
                start_at_gte="2025-01-01T00:00:00",
                start_at_lte="2025-12-31T23:59:59",
            )

            assert result == 10
            mock_filtered.assert_called_once_with("2025-01-01T00:00:00", "2025-12-31T23:59:59")


class TestFilteredSnapshots:
    """Test cases for _filtered_snapshots helper."""

    def test_no_filters(self):
        """Test _filtered_snapshots with no date filters."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_qs = MagicMock()
            mock_annotated = MagicMock()
            mock_filter.return_value.order_by.return_value = mock_qs
            mock_qs.annotate.return_value = mock_annotated

            result = _filtered_snapshots()

            assert result == mock_annotated
            mock_filter.assert_called_once_with(status=Snapshot.Status.COMPLETED)
            mock_filter.return_value.order_by.assert_called_once_with("-created_at")
            mock_qs.filter.assert_not_called()

    def test_with_start_at_gte(self):
        """Test _filtered_snapshots filters by start_at_gte."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_qs = MagicMock()
            mock_annotated = MagicMock()
            mock_filter.return_value.order_by.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.annotate.return_value = mock_annotated

            result = _filtered_snapshots(start_at_gte="2025-01-01T00:00:00")

            assert result == mock_annotated
            mock_filter.return_value.order_by.assert_called_once_with("-created_at")
            mock_qs.filter.assert_called_once_with(
                start_at__gte=datetime.fromisoformat("2025-01-01T00:00:00")
            )

    def test_with_both_filters(self):
        """Test _filtered_snapshots filters by both date bounds."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_qs = MagicMock()
            mock_annotated = MagicMock()
            mock_filter.return_value.order_by.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.annotate.return_value = mock_annotated

            result = _filtered_snapshots(
                start_at_gte="2025-01-01T00:00:00",
                start_at_lte="2025-12-31T23:59:59",
            )

            assert result == mock_annotated
            mock_filter.return_value.order_by.assert_called_once_with("-created_at")
            mock_qs.filter.assert_has_calls(
                [
                    call(start_at__gte=datetime.fromisoformat("2025-01-01T00:00:00")),
                    call(start_at__lte=datetime.fromisoformat("2025-12-31T23:59:59")),
                ]
            )

    def test_with_malformed_date_ignores_filter(self):
        """Test _filtered_snapshots ignores malformed date strings."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_qs = MagicMock()
            mock_annotated = MagicMock()
            mock_filter.return_value.order_by.return_value = mock_qs
            mock_qs.annotate.return_value = mock_annotated

            result = _filtered_snapshots(start_at_gte="not-a-date")

            assert result == mock_annotated
            mock_qs.filter.assert_not_called()

    def test_with_malformed_gte_valid_lte_applies_lte(self):
        """Test _filtered_snapshots applies valid lte even when gte is malformed."""
        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_qs = MagicMock()
            mock_annotated = MagicMock()
            mock_filter.return_value.order_by.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.annotate.return_value = mock_annotated

            result = _filtered_snapshots(
                start_at_gte="not-a-date",
                start_at_lte="2025-12-31T23:59:59",
            )

            assert result == mock_annotated
            mock_qs.filter.assert_called_once_with(
                start_at__lte=datetime.fromisoformat("2025-12-31T23:59:59")
            )
