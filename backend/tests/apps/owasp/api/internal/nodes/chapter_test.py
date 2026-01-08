"""Test cases for ChapterNode."""

from apps.owasp.api.internal.nodes.chapter import ChapterNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestChapterNode(GraphQLNodeBaseTest):
    def test_chapter_node_inheritance(self):
        assert hasattr(ChapterNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ChapterNode.__strawberry_definition__.fields}
        expected_field_names = {
            "contribution_data",
            "contribution_stats",
            "country",
            "created_at",
            "is_active",
            "name",
            "region",
            "summary",
            "key",
            "geo_location",
            "suggested_location",
            "meetup_group",
            "postal_code",
            "tags",
        }
        assert expected_field_names.issubset(field_names)

    def test_resolve_key(self):
        field = self._get_field_by_name("key", ChapterNode)
        assert field is not None
        assert field.type is str

    def test_resolve_country(self):
        field = self._get_field_by_name("country", ChapterNode)
        assert field is not None
        assert field.type is str

    def test_resolve_region(self):
        field = self._get_field_by_name("region", ChapterNode)
        assert field is not None
        assert field.type is str

    def test_resolve_is_active(self):
        field = self._get_field_by_name("is_active", ChapterNode)
        assert field is not None
        assert field.type is bool

    def test_resolve_contribution_data(self):
        field = self._get_field_by_name("contribution_data", ChapterNode)
        assert field is not None
        assert field.type.__class__.__name__ == "NewType"

    def test_resolve_contribution_stats(self):
        field = self._get_field_by_name("contribution_stats", ChapterNode)
        assert field is not None
        assert field.type.__class__.__name__ == "StrawberryOptional"

    def test_contribution_stats_transforms_snake_case_to_camel_case(self):
        """Test that contribution_stats resolver transforms snake_case keys to camelCase."""
        from unittest.mock import Mock

        mock_chapter = Mock()
        mock_chapter.contribution_stats = {
            "commits": 75,
            "pull_requests": 30,
            "issues": 15,
            "releases": 5,
            "total": 125,
        }

        instance = type("BoundNode", (), {})()
        instance.contribution_stats = mock_chapter.contribution_stats

        field = self._get_field_by_name("contribution_stats", ChapterNode)
        result = field.base_resolver.wrapped_func(instance)

        assert result is not None
        assert result["commits"] == 75
        assert result["pullRequests"] == 30
        assert result["issues"] == 15
        assert result["releases"] == 5
        assert result["total"] == 125
        assert "pull_requests" not in result
