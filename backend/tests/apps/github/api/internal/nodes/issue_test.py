"""Test cases for IssueNode."""

from apps.github.api.internal.nodes.issue import IssueNode


class TestIssueNode:
    """Test cases for IssueNode class."""

    def test_issue_node_type(self):
        assert hasattr(IssueNode, "__strawberry_definition__")

    def test_issue_node_fields(self):
        field_names = {field.name for field in IssueNode.__strawberry_definition__.fields}
        expected_field_names = {
            "_id",
            "created_at",
            "state",
            "title",
            "url",
            "author",
            "organization_name",
            "repository_name",
        }
        assert field_names == expected_field_names
