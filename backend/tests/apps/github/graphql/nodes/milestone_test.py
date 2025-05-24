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
            "body",
            "closed_issues_count",
            "created_at",
            "open_issues_count",
            "organization_name",
            "progress",
            "repository_name",
            "title",
            "url",
        }
        assert set(MilestoneNode._meta.fields) == expected_fields
