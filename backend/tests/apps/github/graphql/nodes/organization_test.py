"""Test cases for OrganizationNode."""

from apps.github.graphql.nodes.organization import (
    OrganizationNode,
    OrganizationStatsNode,
)


class TestOrganizationNode:
    def test_organization_node_inheritance(self):
        assert hasattr(OrganizationNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in OrganizationNode.__strawberry_definition__.fields}
        expected_field_names = {
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
        assert field_names == expected_field_names

    def test_resolve_stats(self):
        stats_field = next(
            (f for f in OrganizationNode.__strawberry_definition__.fields if f.name == "stats"),
            None,
        )
        assert stats_field is not None
        assert stats_field.type is OrganizationStatsNode

    def test_resolve_url(self):
        url_field = next(
            (f for f in OrganizationNode.__strawberry_definition__.fields if f.name == "url"), None
        )
        assert url_field is not None
        assert url_field.type is str


class TestOrganizationStatsNode:
    def test_organization_stats_node(self):
        expected_fields = {
            "total_contributors",
            "total_forks",
            "total_issues",
            "total_repositories",
            "total_stars",
        }
        field_names = {
            field.name for field in OrganizationStatsNode.__strawberry_definition__.fields
        }
        assert field_names == expected_fields
