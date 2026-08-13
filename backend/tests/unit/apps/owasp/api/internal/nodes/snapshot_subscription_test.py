"""Test cases for SnapshotSubscriptionNode."""

from unittest.mock import MagicMock

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


class TestSnapshotSubscriptionNodeResolvers:
    """Test SnapshotSubscriptionNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in SnapshotSubscriptionNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_subscribed_projects(self):
        """Test subscribed_projects resolver."""
        resolver = self._get_resolver("subscribed_projects")
        mock_sub = MagicMock()
        mock_p = MagicMock()
        mock_p.pk = 1
        mock_p.name = "Project 1"
        mock_sub.subscribed_projects.all.return_value = [mock_p]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Project 1"

    def test_subscribed_chapters(self):
        """Test subscribed_chapters resolver."""
        resolver = self._get_resolver("subscribed_chapters")
        mock_sub = MagicMock()
        mock_c = MagicMock()
        mock_c.pk = 2
        mock_c.name = "Chapter 1"
        mock_sub.subscribed_chapters.all.return_value = [mock_c]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 2
        assert result[0].name == "Chapter 1"

    def test_subscribed_committees(self):
        """Test subscribed_committees resolver."""
        resolver = self._get_resolver("subscribed_committees")
        mock_sub = MagicMock()
        mock_c = MagicMock()
        mock_c.pk = 3
        mock_c.name = "Committee 1"
        mock_sub.subscribed_committees.all.return_value = [mock_c]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 3
        assert result[0].name == "Committee 1"
