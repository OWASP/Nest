"""Tests for EntitySubscriptionPreferenceNode GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.entity_subscription_preference import (
    EntitySubscriptionPreferenceNode,
)
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestEntitySubscriptionPreferenceNode(GraphQLNodeBaseTest):
    """Test EntitySubscriptionPreferenceNode field resolvers."""

    def test_chapter_resolver(self):
        """Test resolving chapter from preference node."""
        chapter = Mock(spec=Chapter)
        pref = Mock()
        pref.chapter = chapter

        field = self._get_field_by_name("chapter", EntitySubscriptionPreferenceNode)
        result = field.base_resolver.wrapped_func(None, pref)
        assert result == chapter

    def test_chapter_resolver_none(self):
        """Test resolving chapter when none associated."""
        pref = Mock()
        pref.chapter = None

        field = self._get_field_by_name("chapter", EntitySubscriptionPreferenceNode)
        result = field.base_resolver.wrapped_func(None, pref)
        assert result is None

    def test_committee_resolver(self):
        """Test resolving committee from preference node."""
        committee = Mock(spec=Committee)
        pref = Mock()
        pref.committee = committee

        field = self._get_field_by_name("committee", EntitySubscriptionPreferenceNode)
        result = field.base_resolver.wrapped_func(None, pref)
        assert result == committee

    def test_committee_resolver_none(self):
        """Test resolving committee when none associated."""
        pref = Mock()
        pref.committee = None

        field = self._get_field_by_name("committee", EntitySubscriptionPreferenceNode)
        result = field.base_resolver.wrapped_func(None, pref)
        assert result is None

    def test_project_resolver(self):
        """Test resolving project from preference node."""
        project = Mock(spec=Project)
        pref = Mock()
        pref.project = project

        field = self._get_field_by_name("project", EntitySubscriptionPreferenceNode)
        result = field.base_resolver.wrapped_func(None, pref)
        assert result == project

    def test_project_resolver_none(self):
        """Test resolving project when none associated."""
        pref = Mock()
        pref.project = None

        field = self._get_field_by_name("project", EntitySubscriptionPreferenceNode)
        result = field.base_resolver.wrapped_func(None, pref)
        assert result is None
