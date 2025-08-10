"""Test cases for UserNode."""

from apps.github.api.internal.nodes.user import UserNode


class TestUserNode:
    """Test cases for UserNode class."""

    def test_user_node_inheritance(self):
        """Test if UserNode inherits from BaseNode."""
        assert hasattr(UserNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        field_names = {field.name for field in UserNode.__strawberry_definition__.fields}
        expected_field_names = {
            "avatar_url",
            "bio",
            "company",
            "contributions_count",
            "created_at",
            "email",
            "followers_count",
            "following_count",
            "id",
            "is_owasp_staff",
            "issues_count",
            "location",
            "login",
            "name",
            "public_repositories_count",
            "releases_count",
            "updated_at",
            "url",
        }
        assert field_names == expected_field_names
