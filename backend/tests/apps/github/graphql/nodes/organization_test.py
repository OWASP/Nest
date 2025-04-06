"""Test cases for OrganizationNode."""

from graphene import List

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.organization import (
    OrganizationNode,
    OrganizationStatsNode,
)
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.models.organization import Organization


class TestOrganizationNode:
    """Test cases for OrganizationNode class."""

    def test_organization_node_inheritance(self):
        """Test if OrganizationNode inherits from BaseNode."""
        assert issubclass(OrganizationNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert OrganizationNode._meta.model == Organization
        expected_fields = {
            "avatar_url",
            "collaborators_count",
            "company",
            "created_at",
            "description",
            "email",
            "followers_count",
            "location",
            "login",
            "name",
            "updated_at",
            "url",
            "stats",
            "repositories",
            "issues",
            "releases",
            "top_contributors",
        }
        assert set(OrganizationNode._meta.fields) == expected_fields

    def test_resolve_stats(self):
        """Test if stats field is properly configured."""
        stats_field = OrganizationNode._meta.fields.get("stats")
        assert stats_field is not None
        assert stats_field.type == OrganizationStatsNode

    def test_resolve_repositories(self):
        """Test if repositories field is properly configured."""
        repositories_field = OrganizationNode._meta.fields.get("repositories")
        assert repositories_field is not None
        assert repositories_field.type == List(RepositoryNode)

    def test_resolve_issues(self):
        """Test if issues field is properly configured."""
        issues_field = OrganizationNode._meta.fields.get("issues")
        assert issues_field is not None
        assert issues_field.type == List(IssueNode)

    def test_resolve_releases(self):
        """Test if releases field is properly configured."""
        releases_field = OrganizationNode._meta.fields.get("releases")
        assert releases_field is not None
        assert releases_field.type == List(ReleaseNode)

    def test_resolve_top_contributors(self):
        """Test if top_contributors field is properly configured."""
        top_contributors_field = OrganizationNode._meta.fields.get("top_contributors")
        assert top_contributors_field is not None
        assert str(top_contributors_field.type) == "[RepositoryContributorNode]"

    def test_resolve_url(self):
        """Test if url field is properly configured."""
        url_field = OrganizationNode._meta.fields.get("url")
        assert url_field is not None
        assert str(url_field.type) == "String"


class TestOrganizationStatsNode:
    """Test cases for OrganizationStatsNode class."""

    def test_organization_stats_node(self):
        """Test if OrganizationStatsNode has the expected fields."""
        expected_fields = {
            "total_repositories",
            "total_contributors",
            "total_stars",
            "total_forks",
            "total_issues",
        }
        assert set(OrganizationStatsNode._meta.fields) == expected_fields
