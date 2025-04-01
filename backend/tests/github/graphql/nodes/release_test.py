"""Test cases for ReleaseNode."""

from unittest.mock import Mock

from graphene import Field

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.release import Release
from apps.owasp.constants import OWASP_ORGANIZATION_NAME


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

    def test_resolve_project_name(self):
        """Test resolve_project_name method."""
        release_node = ReleaseNode()
        release_node.repository = Mock()
        release_node.repository.project = Mock()

        release_node.repository.project.name = f"{OWASP_ORGANIZATION_NAME}Test Project"
        assert release_node.resolve_project_name(None) == "Test Project"

        release_node.repository.project.name = "Regular Project"
        assert release_node.resolve_project_name(None) == "Regular Project"

    def test_resolve_url(self):
        """Test resolve_url method."""
        release_node = ReleaseNode()
        release_node.url = "https://github.com/owasp/test-repo/releases/tag/v1.0.0"

        assert (
            release_node.resolve_url(None)
            == "https://github.com/owasp/test-repo/releases/tag/v1.0.0"
        )
