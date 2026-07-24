"""Test cases for EntitySubscriptionNode."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.entity_subscription import EntitySubscriptionNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestEntitySubscriptionNode(GraphQLNodeBaseTest):
    """Test cases for EntitySubscriptionNode."""

    def test_entity_subscription_node_has_definition(self):
        """Test EntitySubscriptionNode has strawberry definition."""
        assert hasattr(EntitySubscriptionNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {
            field.name for field in EntitySubscriptionNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "created_at",
            "entity_preferences",
            "frequency",
            "is_active",
            "name",
            "updated_at",
        }
        assert expected_field_names.issubset(field_names)

    def test_entity_preferences_resolver(self):
        """Test resolving entity preferences."""
        mock_sub = Mock()
        mock_prefs = [Mock(), Mock()]
        mock_sub.entity_preferences.all.return_value = mock_prefs

        field = self._get_field_by_name("entity_preferences", EntitySubscriptionNode)
        result = field.base_resolver.wrapped_func(None, mock_sub)

        assert result == mock_prefs
