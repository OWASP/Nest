"""Test cases for UserNode."""

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.user import User


class TestUserNode:
    """Test cases for UserNode class."""

    def test_user_node_inheritance(self):
        """Test if UserNode inherits from BaseNode."""
        assert issubclass(UserNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert UserNode._meta.model == User
        expected_fields = {
            "avatar_url",
            "bio",
            "company",
            "contributions_count",
            "created_at",
            "email",
            "followers_count",
            "following_count",
            "id",
            "issues_count",
            "issues",
            "location",
            "login",
            "name",
            "public_repositories_count",
            "releases_count",
            "releases",
            "updated_at",
            "url",
        }
        assert set(UserNode._meta.fields) == expected_fields
