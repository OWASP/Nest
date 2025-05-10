"""Test cases for MilestoneNode."""

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.milestone import MilestoneNode
from apps.github.models.milestone import Milestone


class TestMilestoneNode:
    """Test cases for MilestoneNode class."""

    def test_milestone_node_inheritance(self):
        """Test if IssueNode inherits from BaseNode."""
        assert issubclass(MilestoneNode, BaseNode)

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        assert MilestoneNode._meta.model == Milestone
        expected_fields = {
            "author",
            "created_at",
            "title",
            "open_issues_count",
            "closed_issues_count",
            "url",
            "repository_name",
            "organization_name",
        }
        assert set(MilestoneNode._meta.fields) == expected_fields
