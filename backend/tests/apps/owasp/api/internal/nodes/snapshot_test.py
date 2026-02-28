"""Test cases for SnapshotNode."""

from unittest.mock import MagicMock

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestSnapshotNode(GraphQLNodeBaseTest):
    """Test cases for SnapshotNode."""

    def test_snapshot_node_inheritance(self):
        """Test SnapshotNode has strawberry definition."""
        assert hasattr(SnapshotNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {field.name for field in SnapshotNode.__strawberry_definition__.fields}
        expected_field_names = {
            "created_at",
            "end_at",
            "key",
            "new_chapters",
            "new_issues",
            "new_projects",
            "new_releases",
            "new_users",
            "start_at",
            "title",
        }
        assert expected_field_names.issubset(field_names)


class TestSnapshotNodeResolvers:
    """Test SnapshotNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in SnapshotNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_key_resolver(self):
        """Test key resolver returns snapshot key."""
        resolver = self._get_resolver("key")
        mock_snapshot = MagicMock()
        mock_snapshot.key = "2025-02"

        result = resolver(None, mock_snapshot)

        assert result == "2025-02"

    def test_new_issues_resolver(self):
        """Test new_issues resolver returns ordered issues."""
        resolver = self._get_resolver("new_issues")
        mock_snapshot = MagicMock()
        mock_issues = [MagicMock(), MagicMock()]
        mock_snapshot.new_issues.order_by.return_value.__getitem__.return_value = mock_issues

        result = resolver(None, mock_snapshot)

        mock_snapshot.new_issues.order_by.assert_called_once_with("-created_at")
        assert result == mock_issues

    def test_new_projects_resolver(self):
        """Test new_projects resolver returns ordered projects."""
        resolver = self._get_resolver("new_projects")
        mock_snapshot = MagicMock()
        mock_projects = [MagicMock(), MagicMock()]
        mock_snapshot.new_projects.order_by.return_value = mock_projects

        result = resolver(None, mock_snapshot)

        mock_snapshot.new_projects.order_by.assert_called_once_with("-created_at")
        assert result == mock_projects

    def test_new_releases_resolver(self):
        """Test new_releases resolver returns ordered releases."""
        resolver = self._get_resolver("new_releases")
        mock_snapshot = MagicMock()
        mock_releases = [MagicMock(), MagicMock()]
        mock_snapshot.new_releases.order_by.return_value = mock_releases

        result = resolver(None, mock_snapshot)

        mock_snapshot.new_releases.order_by.assert_called_once_with("-published_at")
        assert result == mock_releases

    def test_new_users_resolver(self):
        """Test new_users resolver returns ordered users."""
        resolver = self._get_resolver("new_users")
        mock_snapshot = MagicMock()
        mock_users = [MagicMock(), MagicMock()]
        mock_snapshot.new_users.order_by.return_value = mock_users

        result = resolver(None, mock_snapshot)

        mock_snapshot.new_users.order_by.assert_called_once_with("-created_at")
        assert result == mock_users
