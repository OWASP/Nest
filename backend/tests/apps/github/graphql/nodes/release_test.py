"""Test cases for ReleaseNode."""

from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.user import UserNode


class TestReleaseNode:
    """Test cases for ReleaseNode class."""

    def test_release_node_inheritance(self):
        assert hasattr(ReleaseNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ReleaseNode.__strawberry_definition__.fields}
        expected_field_names = {
            "author",
            "is_pre_release",
            "name",
            "organization_name",
            "project_name",
            "published_at",
            "repository_name",
            "tag_name",
            "url",
        }
        assert field_names == expected_field_names

    def test_author_field(self):
        fields = ReleaseNode.__strawberry_definition__.fields
        author_field = next((field for field in fields if field.name == "author"), None)
        assert author_field is not None
        assert author_field.type.of_type is UserNode
