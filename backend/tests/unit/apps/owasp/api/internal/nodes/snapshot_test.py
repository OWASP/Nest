"""Test cases for SnapshotNode."""

from unittest.mock import MagicMock

from apps.github.api.internal.nodes.issue import MERGED_PULL_REQUESTS_PREFETCH
from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestSnapshotNode(GraphQLNodeBaseTest):
    """Test cases for SnapshotNode."""

    def test_snapshot_node_inheritance(self):
        """Test SnapshotNode has strawberry definition."""
        assert hasattr(SnapshotNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {field.name for field in SnapshotNode.__strawberry_definition__.fields}
        expected_field_names = {
            "chapters",
            "created_at",
            "end_at",
            "events",
            "issues",
            "key",
            "posts",
            "projects",
            "pull_requests",
            "releases",
            "start_at",
            "title",
            "users",
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

    def test_events_resolver(self):
        """Test events resolver returns ordered events."""
        resolver = self._get_resolver("events")
        mock_snapshot = MagicMock()
        mock_events = [MagicMock(), MagicMock()]
        mock_snapshot.events.order_by.return_value = mock_events

        result = resolver(None, mock_snapshot)

        mock_snapshot.events.order_by.assert_called_once_with("-start_date")
        assert result == mock_events

    def test_issues_resolver(self):
        """Test issues resolver returns ordered issues."""
        resolver = self._get_resolver("issues")
        mock_snapshot = MagicMock()
        mock_issues = [MagicMock(), MagicMock()]
        prefetch_mock = mock_snapshot.issues.prefetch_related.return_value
        prefetch_mock.order_by.return_value.__getitem__.return_value = mock_issues

        result = resolver(None, mock_snapshot)

        mock_snapshot.issues.prefetch_related.assert_called_once_with(
            MERGED_PULL_REQUESTS_PREFETCH
        )
        prefetch_mock.order_by.assert_called_once_with("-created_at")
        assert result == mock_issues

    def test_posts_resolver(self):
        """Test posts resolver returns ordered posts."""
        resolver = self._get_resolver("posts")
        mock_snapshot = MagicMock()
        mock_posts = [MagicMock(), MagicMock()]
        mock_snapshot.posts.order_by.return_value = mock_posts

        result = resolver(None, mock_snapshot)

        mock_snapshot.posts.order_by.assert_called_once_with("-published_at")
        assert result == mock_posts

    def test_projects_resolver(self):
        """Test projects resolver returns ordered projects."""
        resolver = self._get_resolver("projects")
        mock_snapshot = MagicMock()
        mock_projects = [MagicMock(), MagicMock()]
        mock_snapshot.projects.order_by.return_value = mock_projects

        result = resolver(None, mock_snapshot)

        mock_snapshot.projects.order_by.assert_called_once_with("-created_at")
        assert result == mock_projects

    def test_pull_requests_resolver(self):
        """Test pull_requests resolver returns ordered pull requests."""
        resolver = self._get_resolver("pull_requests")
        mock_snapshot = MagicMock()
        mock_prs = [MagicMock(), MagicMock()]
        mock_snapshot.pull_requests.order_by.return_value = mock_prs

        result = resolver(None, mock_snapshot)

        mock_snapshot.pull_requests.order_by.assert_called_once_with("-created_at")
        assert result == mock_prs

    def test_releases_resolver(self):
        """Test releases resolver returns ordered releases."""
        resolver = self._get_resolver("releases")
        mock_snapshot = MagicMock()
        mock_releases = [MagicMock(), MagicMock()]
        mock_snapshot.releases.order_by.return_value = mock_releases

        result = resolver(None, mock_snapshot)

        mock_snapshot.releases.order_by.assert_called_once_with("-published_at")
        assert result == mock_releases

    def test_users_resolver(self):
        """Test users resolver returns ordered users."""
        resolver = self._get_resolver("users")
        mock_snapshot = MagicMock()
        mock_users = [MagicMock(), MagicMock()]
        mock_snapshot.users.order_by.return_value = mock_users

        result = resolver(None, mock_snapshot)

        mock_snapshot.users.order_by.assert_called_once_with("-created_at")
        assert result == mock_users
