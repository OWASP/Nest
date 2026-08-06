"""Test cases for SnapshotSubscriptionNode."""

from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode


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
            "updated_at",
        }
        assert expected_field_names.issubset(field_names)
