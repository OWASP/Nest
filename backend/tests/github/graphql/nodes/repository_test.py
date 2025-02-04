"""Test cases for RepositoryNode."""

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.models.repository import Repository


class TestRepositoryNode:
    """Test cases for RepositoryNode class."""

    def test_repository_node_inheritance(self):
        """Test if RepositoryNode inherits from BaseNode."""
        assert issubclass(RepositoryNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert RepositoryNode._meta.model == Repository
        expected_fields = {
            "contributors_count",
            "forks_count",
            "name",
            "open_issues_count",
            "stars_count",
            "subscribers_count",
            "url",
        }
        assert set(RepositoryNode._meta.fields) == expected_fields

    def test_resolve_url_field(self, mocker):
        """Test if URL field is properly defined."""
        field = RepositoryNode._meta.fields.get("url")
        assert field is not None
        assert str(field.type) == "String"
