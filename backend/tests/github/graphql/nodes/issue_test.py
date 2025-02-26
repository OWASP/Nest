"""Test cases for IssueNode."""

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.models.issue import Issue


class TestIssueNode:
    """Test cases for IssueNode class."""

    def test_issue_node_inheritance(self):
        """Test if IssueNode inherits from BaseNode."""
        assert issubclass(IssueNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert IssueNode._meta.model == Issue
        expected_fields = {
            "author",
            "comments_count",
            "created_at",
            "number",
            "state",
            "url",
            "title",
        }
        assert set(IssueNode._meta.fields) == expected_fields
