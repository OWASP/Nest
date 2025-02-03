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
            "name",
            "forks_count",
            "stars_count",
            "open_issues_count",
            "subscribers_count",
            "contributors_count",
            "repository_url",
        }
        assert set(RepositoryNode._meta.fields) == expected_fields

    def test_repository_url_field(self):
        """Test if repository_url field is properly defined."""
        field = RepositoryNode._meta.fields.get("repository_url")
        assert field is not None
        assert str(field.type) == "String"

    def test_resolve_repository_url_none(self, mocker):
        """Test resolution of repository_url field with missing attributes."""
        repository = mocker.Mock()
        repository.name = "repo"

        node = RepositoryNode(repository)
        resolved_url = node.resolve_repository_url(None)

        assert resolved_url is None
