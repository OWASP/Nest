"""Test cases for MilestoneNode."""

from apps.github.graphql.nodes.milestone import MilestoneNode


class TestMilestoneNode:
    """Test cases for MilestoneNode class."""

    def test_milestone_node_type(self):
        assert hasattr(MilestoneNode, "__strawberry_definition__")

    def test_milestone_node_fields(self):
        fields = MilestoneNode.__strawberry_definition__.fields
        field_names = {field.name for field in fields}
        expected_fields = {
            "author",
            "closed_issues_count",
            "created_at",
            "open_issues_count",
            "organization_name",
            "repository_name",
            "title",
            "url",
        }
        assert field_names == expected_fields
