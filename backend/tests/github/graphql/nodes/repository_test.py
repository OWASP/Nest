"""Test cases for RepositoryNode."""

from graphene import List

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
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
            "commits_count",
            "contributors_count",
            "created_at",
            "description",
            "forks_count",
            "issues",
            "languages",
            "license",
            "name",
            "project",
            "open_issues_count",
            "size",
            "stars_count",
            "subscribers_count",
            "topics",
            "top_contributors",
            "updated_at",
            "url",
            "releases",
        }
        assert set(RepositoryNode._meta.fields) == expected_fields

    def test_resolve_url_field(self, mocker):
        """Test if URL field is properly defined."""
        field = RepositoryNode._meta.fields.get("url")
        assert field is not None
        assert str(field.type) == "String"

    def test_resolve_top_contributors_field(self, mocker):
        """Resolve topContributors."""
        field = RepositoryNode._meta.fields.get("top_contributors")
        assert field is not None
        assert str(field.type) == "[ContributorType]"

    def test_resolve_languages_field(self, mocker):
        """Resolve languages."""
        field = RepositoryNode._meta.fields.get("languages")
        assert field is not None
        assert str(field.type) == "[String]"

    def test_resolve_topics_field(self, mocker):
        """Resolve topics."""
        field = RepositoryNode._meta.fields.get("topics")
        assert field is not None
        assert str(field.type) == "[String]"

    def test_issues_field(self, mocker):
        """Resolve recent issues."""
        field = RepositoryNode._meta.fields.get("issues")
        assert field is not None
        assert field.type == List(IssueNode)

    def test_releases_field(self, mocker):
        """Resolve recent releases."""
        field = RepositoryNode._meta.fields.get("releases")
        assert field is not None
        assert field.type == List(ReleaseNode)
