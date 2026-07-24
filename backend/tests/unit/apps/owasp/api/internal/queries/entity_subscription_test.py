"""Tests for entity subscription GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.entity_subscription import EntitySubscriptionQuery


def mock_info(*, authenticated=True):
    """Return a minimal mock of strawberry Info with request on context."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user.is_authenticated = authenticated
    return info


class TestEntitySubscriptionQuery:
    """Test cases for EntitySubscriptionQuery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.query = EntitySubscriptionQuery()

    def test_query_has_strawberry_definition(self):
        """Check if EntitySubscriptionQuery has valid Strawberry definition."""
        assert hasattr(EntitySubscriptionQuery, "__strawberry_definition__")

        field_names = [
            field.name for field in EntitySubscriptionQuery.__strawberry_definition__.fields
        ]
        assert "my_entity_subscriptions" in field_names

    def _resolve_my_entity_subscriptions(self, info):
        """Invoke the underlying resolver for my_entity_subscriptions."""
        field = EntitySubscriptionQuery.__dict__["my_entity_subscriptions"]
        return field(self.query, info=info)

    def test_my_entity_subscriptions_unauthenticated(self):
        """Test myEntitySubscriptions returns empty list for unauthenticated user."""
        info = mock_info(authenticated=False)
        result = self._resolve_my_entity_subscriptions(info)
        assert result == []

    def test_my_entity_subscriptions_found(self):
        """Test myEntitySubscriptions returns subscriptions when they exist."""
        info = mock_info()
        mock_queryset = MagicMock()
        with patch(
            "apps.owasp.api.internal.queries.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.filter.return_value = mock_queryset
            result = self._resolve_my_entity_subscriptions(info)
            assert result == mock_queryset
            mock_objects.filter.assert_called_once_with(user=info.context.request.user)
