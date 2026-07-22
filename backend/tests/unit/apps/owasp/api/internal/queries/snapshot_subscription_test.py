"""Tests for snapshot subscription GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.snapshot_subscription import SnapshotSubscriptionQuery


def mock_info(*, authenticated=True):
    """Return a minimal mock of strawberry Info with request on context."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user.is_authenticated = authenticated
    return info


class TestSnapshotSubscriptionQuery:
    """Test cases for SnapshotSubscriptionQuery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.query = SnapshotSubscriptionQuery()

    def test_query_has_strawberry_definition(self):
        """Check if SnapshotSubscriptionQuery has valid Strawberry definition."""
        assert hasattr(SnapshotSubscriptionQuery, "__strawberry_definition__")

        field_names = [
            field.name for field in SnapshotSubscriptionQuery.__strawberry_definition__.fields
        ]
        assert "my_snapshot_subscription" in field_names

    def _resolve_my_snapshot_subscription(self, info):
        """Invoke the underlying resolver for my_snapshot_subscription."""
        field = SnapshotSubscriptionQuery.__dict__["my_snapshot_subscription"]
        return field(self.query, info=info)

    def test_my_snapshot_subscription_unauthenticated(self):
        """Test my_snapshot_subscription returns None for unauthenticated user."""
        info = mock_info(authenticated=False)
        result = self._resolve_my_snapshot_subscription(info)
        assert result is None

    def test_my_snapshot_subscription_found(self):
        """Test my_snapshot_subscription returns subscription when it exists."""
        info = mock_info()
        mock_qs = MagicMock()
        mock_sub = MagicMock()
        mock_qs.first.return_value = mock_sub
        with patch(
            "apps.owasp.api.internal.queries.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.filter.return_value = mock_qs
            result = self._resolve_my_snapshot_subscription(info)
            assert result == mock_sub
            mock_objects.filter.assert_called_once_with(user=info.context.request.user)
