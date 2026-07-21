"""Test cases for EntitySubscriptionNode."""

from apps.owasp.api.internal.nodes.entity_subscription import EntitySubscriptionNode


class TestEntitySubscriptionNode:
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
