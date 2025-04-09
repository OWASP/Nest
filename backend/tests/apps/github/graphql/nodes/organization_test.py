"""Test cases for OrganizationNode."""

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.organization import (
    OrganizationNode,
    OrganizationStatsNode,
)
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
            "stats",
            "updated_at",
            "url",
        }
        assert set(OrganizationNode._meta.fields) == expected_fields

    def test_resolve_stats(self):
        """Test if stats field is properly configured."""
        stats_field = OrganizationNode._meta.fields.get("stats")
        assert stats_field is not None
        assert stats_field.type == OrganizationStatsNode

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
            "total_contributors",
            "total_forks",
            "total_issues",
            "total_repositories",
            "total_stars",
        }
        assert set(OrganizationStatsNode._meta.fields) == expected_fields
