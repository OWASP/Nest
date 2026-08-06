"""Test cases for EntitySubscriptionNode."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.entity_subscription import EntitySubscriptionNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestEntitySubscriptionNode(GraphQLNodeBaseTest):
    """Test cases for EntitySubscriptionNode."""

    def test_entity_subscription_node_has_definition(self):
        """Test EntitySubscriptionNode has strawberry definition."""
        assert hasattr(EntitySubscriptionNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {
            field.name for field in EntitySubscriptionNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "chapter",
            "committee",
            "created_at",
            "frequency",
            "is_active",
            "project",
            "updated_at",
        }
        assert expected_field_names.issubset(field_names)

    def test_chapter_resolver(self):
        """Test resolving chapter."""
        mock_sub = Mock()
        mock_chapter = Mock()
        mock_sub.chapter = mock_chapter

        field = self._get_field_by_name("chapter", EntitySubscriptionNode)
        result = field.base_resolver.wrapped_func(None, mock_sub)

        assert result == mock_chapter

    def test_committee_resolver(self):
        """Test resolving committee."""
        mock_sub = Mock()
        mock_committee = Mock()
        mock_sub.committee = mock_committee

        field = self._get_field_by_name("committee", EntitySubscriptionNode)
        result = field.base_resolver.wrapped_func(None, mock_sub)

        assert result == mock_committee

    def test_project_resolver(self):
        """Test resolving project."""
        mock_sub = Mock()
        mock_project = Mock()
        mock_sub.project = mock_project

        field = self._get_field_by_name("project", EntitySubscriptionNode)
        result = field.base_resolver.wrapped_func(None, mock_sub)

        assert result == mock_project
