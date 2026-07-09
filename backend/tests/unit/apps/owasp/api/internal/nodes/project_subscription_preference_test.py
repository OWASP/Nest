"""Test cases for ProjectSubscriptionPreferenceNode."""

from apps.owasp.api.internal.nodes.project_subscription_preference import (
    ProjectSubscriptionPreferenceNode,
)
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestProjectSubscriptionPreferenceNode(GraphQLNodeBaseTest):
    """Test cases for ProjectSubscriptionPreferenceNode."""

    def test_project_subscription_preference_node_inheritance(self):
        """Test ProjectSubscriptionPreferenceNode has strawberry definition."""
        assert hasattr(ProjectSubscriptionPreferenceNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {
            field.name
            for field in ProjectSubscriptionPreferenceNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "include_issues",
            "include_pull_requests",
            "include_releases",
            "project",
        }
        assert expected_field_names.issubset(field_names)
