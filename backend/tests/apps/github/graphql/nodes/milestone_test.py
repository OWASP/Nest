"""Test cases for MilestoneNode."""

from apps.github.graphql.nodes.milestone import MilestoneNode


class TestMilestoneNode:
    """Test cases for MilestoneNode class."""

    def test_milestone_node_type(self):
        assert hasattr(MilestoneNode, "__strawberry_definition__")

    def test_milestone_node_fields(self):
        field_names = {field.name for field in MilestoneNode.__strawberry_definition__.fields}
        expected_field_names = {
            "author",
            "body",
            "closed_issues_count",
            "created_at",
            "open_issues_count",
            "organization_name",
            "progress",
            "repository_name",
            "state",
            "title",
            "url",
        }
        assert field_names == expected_field_names
