from apps.nest.api.internal.nodes.user import AuthUserNode


class TestGitHubAuthResult:
    """Test cases for GitHubAuthResult."""

    def test_auth_user_node_configuration(self):
        """Test user node configuration."""
        assert AuthUserNode.__strawberry_definition__.name == "AuthUserNode"

        fields = {f.name: f for f in AuthUserNode.__strawberry_definition__.fields}
        assert set(fields.keys()) == {"is_owasp_staff", "username"}

        username_field = fields["username"]
        is_owasp_staff_field = fields["is_owasp_staff"]
        assert username_field.type is str or getattr(username_field.type, "of_type", None) is str
        assert (
            is_owasp_staff_field.type is bool
            or getattr(is_owasp_staff_field.type, "of_type", None) is bool
        )
