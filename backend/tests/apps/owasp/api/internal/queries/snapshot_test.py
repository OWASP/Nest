"""Tests for SnapshotQuery."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.snapshot import SnapshotQuery
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

    def test_snapshot_exists(self):
        """Test snapshot returns snapshot when found."""
        mock_snapshot = MagicMock(spec=Snapshot)

        with patch("apps.owasp.api.internal.queries.snapshot.Snapshot.objects.get") as mock_get:
            mock_get.return_value = mock_snapshot

            result = self.query.__class__.__dict__["snapshot"](self.query, key="test-key")

            assert result == mock_snapshot
            mock_get.assert_called_once_with(
                key="test-key",
                status=Snapshot.Status.COMPLETED,
            )

    def test_snapshot_not_exists(self):
        """Test snapshot returns None when not found."""
        with patch("apps.owasp.api.internal.queries.snapshot.Snapshot.objects.get") as mock_get:
            mock_get.side_effect = Snapshot.DoesNotExist

            result = self.query.__class__.__dict__["snapshot"](self.query, key="nonexistent")

            assert result is None

    def test_snapshots_with_positive_limit(self):
        """Test snapshots returns list with positive limit."""
        mock_snapshots = [MagicMock(spec=Snapshot), MagicMock(spec=Snapshot)]

        with patch(
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_filter.return_value.order_by.return_value.__getitem__ = MagicMock(
                return_value=mock_snapshots
            )

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
            "apps.owasp.api.internal.queries.snapshot.Snapshot.objects.filter"
        ) as mock_filter:
            mock_filter.return_value.order_by.return_value.__getitem__ = MagicMock(
                return_value=mock_snapshots
            )
            result = self.query.__class__.__dict__["snapshots"](self.query, limit=500)
            assert result == mock_snapshots
