"""Test cases for SnapshotFeedbackNode."""

from unittest.mock import MagicMock

from apps.owasp.api.internal.nodes.snapshot_feedback import SnapshotFeedbackNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestSnapshotFeedbackNode(GraphQLNodeBaseTest):
    """Test cases for SnapshotFeedbackNode."""

    def test_snapshot_feedback_node_inheritance(self):
        """Test SnapshotFeedbackNode has strawberry definition."""
        assert hasattr(SnapshotFeedbackNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {
            field.name for field in SnapshotFeedbackNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "avatar_url",
            "comment",
            "created_at",
            "login",
            "rating",
            "updated_at",
            "username",
        }

        assert expected_field_names.issubset(field_names)

    def test_does_not_expose_user_object(self):
        """Test the raw user relation is not exposed, only the username."""
        field_names = {
            field.name for field in SnapshotFeedbackNode.__strawberry_definition__.fields
        }

        assert "user" not in field_names


class TestSnapshotFeedbackNodeResolvers:
    """Test SnapshotFeedbackNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in SnapshotFeedbackNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_username_resolver(self):
        """Test username resolver returns the author's username."""
        resolver = self._get_resolver("username")
        feedback = MagicMock()
        feedback.user.username = "alice"

        assert resolver(None, feedback) == "alice"

    def test_avatar_url_resolver(self):
        """Test avatar_url resolver returns the linked GitHub avatar."""
        resolver = self._get_resolver("avatar_url")
        feedback = MagicMock()
        feedback.user.github_user.avatar_url = "https://avatars.githubusercontent.com/u/1?v=4"

        assert resolver(None, feedback) == "https://avatars.githubusercontent.com/u/1?v=4"

    def test_avatar_url_resolver_without_github_user(self):
        """Test avatar_url resolver returns an empty string when no GitHub account is linked."""
        resolver = self._get_resolver("avatar_url")
        feedback = MagicMock()
        feedback.user.github_user = None

        assert resolver(None, feedback) == ""

    def test_login_resolver(self):
        """Test login resolver returns the linked GitHub login."""
        resolver = self._get_resolver("login")
        feedback = MagicMock()
        feedback.user.github_user.login = "alice"

        assert resolver(None, feedback) == "alice"

    def test_login_resolver_without_github_user(self):
        """Test login resolver returns an empty string when no GitHub account is linked."""
        resolver = self._get_resolver("login")
        feedback = MagicMock()
        feedback.user.github_user = None

        assert resolver(None, feedback) == ""
