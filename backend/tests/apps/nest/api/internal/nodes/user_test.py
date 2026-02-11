from unittest.mock import Mock

from apps.nest.api.internal.nodes.user import AuthUserNode


class TestGitHubAuthResult:
    """Test cases for GitHubAuthResult."""

    def test_auth_user_node_configuration(self):
        """Test user node configuration."""
        assert AuthUserNode.__strawberry_definition__.name == "AuthUserNode"

        fields = {f.name: f for f in AuthUserNode.__strawberry_definition__.fields}
        assert set(fields.keys()) == {"_id", "is_owasp_staff", "username"}

        username_field = fields["username"]
        is_owasp_staff_field = fields["is_owasp_staff"]
        assert username_field.type is str or getattr(username_field.type, "of_type", None) is str
        assert (
            is_owasp_staff_field.type is bool
            or getattr(is_owasp_staff_field.type, "of_type", None) is bool
        )

    def test_is_owasp_staff_with_no_github_user(self):
        """Test is_owasp_staff returns False when github_user is None."""
        # Create a simple object to act as self
        class FakeNode:
            github_user = None

        node = FakeNode()
        
        # Get the raw function from the strawberry field
        raw_func = AuthUserNode.__strawberry_definition__.get_field("is_owasp_staff").base_resolver.wrapped_func
        result = raw_func(node)
        assert result is False

    def test_is_owasp_staff_with_github_user_true(self):
        """Test is_owasp_staff returns True when github_user.is_owasp_staff is True."""
        class FakeNode:
            pass

        mock_github_user = Mock()
        mock_github_user.is_owasp_staff = True

        node = FakeNode()
        node.github_user = mock_github_user

        # Get the raw function from the strawberry field
        raw_func = AuthUserNode.__strawberry_definition__.get_field("is_owasp_staff").base_resolver.wrapped_func
        result = raw_func(node)
        assert result is True

    def test_is_owasp_staff_with_github_user_false(self):
        """Test is_owasp_staff returns False when github_user.is_owasp_staff is False."""
        class FakeNode:
            pass

        mock_github_user = Mock()
        mock_github_user.is_owasp_staff = False

        node = FakeNode()
        node.github_user = mock_github_user

        # Get the raw function from the strawberry field
        raw_func = AuthUserNode.__strawberry_definition__.get_field("is_owasp_staff").base_resolver.wrapped_func
        result = raw_func(node)
        assert result is False
