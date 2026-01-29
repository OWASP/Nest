"""Test cases for MenteeNode."""

from unittest.mock import Mock

from apps.mentorship.api.internal.nodes.mentee import MenteeNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestMenteeNode(GraphQLNodeBaseTest):
    """Test cases for MenteeNode class."""

    def test_mentee_node_inheritance(self):
        """Test if MenteeNode inherits from BaseNode."""
        assert hasattr(MenteeNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        field_names = {field.name for field in MenteeNode.__strawberry_definition__.fields}
        expected_field_names = {
            "avatar_url",
            "bio",
            "domains",
            "experience_level",
            # "id", # id is handled by relay.Node and may not appear in basic field introspection
            "login",
            "name",
            "tags",
        }
        # Note: id is added by strawberry.relay.Node

        missing = expected_field_names - field_names
        assert not missing, f"Missing fields on MenteeNode: {sorted(missing)}"

    def test_avatar_url_field(self):
        """Test avatar_url field resolution."""
        mock_mentee = Mock()
        mock_mentee.github_user.avatar_url = "https://example.com/avatar.jpg"

        field = self._get_field_by_name("avatar_url", MenteeNode)
        # Using the resolver directly
        result = field.base_resolver.wrapped_func(None, mock_mentee)
        assert result == "https://example.com/avatar.jpg"

    def test_bio_field(self):
        """Test bio field resolution."""
        mock_mentee = Mock()
        mock_mentee.github_user.bio = "Test Bio"

        field = self._get_field_by_name("bio", MenteeNode)
        result = field.base_resolver.wrapped_func(None, mock_mentee)
        assert result == "Test Bio"

    def test_login_field(self):
        """Test login field resolution."""
        mock_mentee = Mock()
        mock_mentee.github_user.login = "testuser"

        field = self._get_field_by_name("login", MenteeNode)
        result = field.base_resolver.wrapped_func(None, mock_mentee)
        assert result == "testuser"

    def test_name_field_with_name(self):
        """Test name field resolution when name exists."""
        mock_mentee = Mock()
        mock_mentee.github_user.name = "Test User"
        mock_mentee.github_user.login = "testuser"

        field = self._get_field_by_name("name", MenteeNode)
        result = field.base_resolver.wrapped_func(None, mock_mentee)
        assert result == "Test User"

    def test_name_field_fallback_to_login(self):
        """Test name field resolution fallback to login when name is missing."""
        mock_mentee = Mock()
        mock_mentee.github_user.name = None
        mock_mentee.github_user.login = "testuser"

        field = self._get_field_by_name("name", MenteeNode)
        result = field.base_resolver.wrapped_func(None, mock_mentee)
        assert result == "testuser"
