"""Tests for snapshot subscription GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.snapshot_subscription import SnapshotSubscriptionQuery
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


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
        assert "my_snapshot_subscriptions" in field_names

    def test_my_snapshot_subscriptions_unauthenticated(self):
        """Test my_snapshot_subscriptions returns empty list for unauthenticated user."""
        info = mock_info(authenticated=False)
        result = self.query.my_snapshot_subscriptions(info=info)
        assert result == []

    def test_my_snapshot_subscriptions_returns_list(self):
        """Test my_snapshot_subscriptions returns list of subscriptions."""
        info = mock_info()
        mock_sub1 = MagicMock()
        mock_sub2 = MagicMock()
        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_sub1, mock_sub2]
        with patch(
            "apps.owasp.api.internal.queries.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.filter.return_value = mock_qs
            result = self.query.my_snapshot_subscriptions(info=info)
            assert result == [mock_sub1, mock_sub2]
            mock_objects.filter.assert_called_once_with(user=info.context.request.user)

    def _resolve_subscription_by_token(self, token):
        """Invoke the underlying resolver for subscription_by_token."""
        field = SnapshotSubscriptionQuery.__dict__["subscription_by_token"]
        return field(self.query, token=token)

    @patch("apps.owasp.api.internal.queries.snapshot_subscription.SnapshotSubscription.objects")
    def test_subscription_by_token_found(self, mock_objects):
        """Test subscription_by_token returns subscription when token matches."""
        mock_sub = MagicMock()
        mock_objects.get.return_value = mock_sub
        result = self._resolve_subscription_by_token("abc-123-uuid")
        assert result == mock_sub
        mock_objects.get.assert_called_once_with(unsubscribe_token="abc-123-uuid")  # noqa: S106

    @patch("apps.owasp.api.internal.queries.snapshot_subscription.SnapshotSubscription.objects")
    def test_subscription_by_token_not_found(self, mock_objects):
        """Test subscription_by_token returns None when token doesn't match."""
        mock_objects.get.side_effect = SnapshotSubscription.DoesNotExist
        result = self._resolve_subscription_by_token("nonexistent-token")
        assert result is None

    @patch("apps.owasp.api.internal.queries.snapshot_subscription.SnapshotSubscription.objects")
    def test_subscription_by_token_invalid_uuid(self, mock_objects):
        """Test subscription_by_token returns None for invalid UUID."""
        mock_objects.get.side_effect = ValueError("invalid UUID")
        result = self._resolve_subscription_by_token("not-a-uuid")
        assert result is None
