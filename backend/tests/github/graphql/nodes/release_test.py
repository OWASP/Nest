"""Test cases for ReleaseNode."""

from graphene import Field

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.release import Release


class TestReleaseNode:
    """Test cases for ReleaseNode class."""

    def test_release_node_inheritance(self):
        """Test if ReleaseNode inherits from BaseNode."""
        assert issubclass(ReleaseNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert ReleaseNode._meta.model == Release
        expected_fields = {
            "author",
            "is_pre_release",
            "name",
            "project_name",
            "published_at",
            "tag_name",
            "url",
        }
        assert set(ReleaseNode._meta.fields) == expected_fields

    def test_author_field(self):
        """Test if author field is properly configured."""
        author_field = ReleaseNode._meta.fields.get("author")
        assert isinstance(author_field, Field)
        assert author_field.type == UserNode
