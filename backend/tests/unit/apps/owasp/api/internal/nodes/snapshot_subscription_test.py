"""Test cases for SnapshotSubscriptionNode."""

from apps.owasp.api.internal.nodes.snapshot_subscription import (
    SnapshotSubscriptionNode,
    SubscribedEntityNode,
)


class TestSubscribedEntityNode:
    """Test cases for SubscribedEntityNode."""

    def test_subscribed_entity_node_has_id_and_name(self):
        """Test SubscribedEntityNode can be instantiated with id and name."""
        node = SubscribedEntityNode(id=1, name="Test Entity")
        assert node.id == 1
        assert node.name == "Test Entity"


class TestSnapshotSubscriptionNode:
    """Test cases for SnapshotSubscriptionNode."""

    def test_snapshot_subscription_node_has_definition(self):
        """Test SnapshotSubscriptionNode has strawberry definition."""
        assert hasattr(SnapshotSubscriptionNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {
            field.name for field in SnapshotSubscriptionNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "created_at",
            "frequency",
            "include_chapters",
            "include_events",
            "include_issues",
            "include_posts",
            "include_projects",
            "include_pull_requests",
            "include_releases",
            "include_users",
            "is_active",
            "name",
            "subscribed_chapters",
            "subscribed_committees",
            "subscribed_projects",
            "updated_at",
        }
        assert expected_field_names.issubset(field_names)
