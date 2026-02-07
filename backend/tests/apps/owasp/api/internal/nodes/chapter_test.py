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
        result = field.base_resolver.wrapped_func(None, instance)

        assert result is not None
        assert result["commits"] == 75
        assert result["pullRequests"] == 30
        assert result["issues"] == 15
        assert result["releases"] == 5
        assert result["total"] == 125
        assert "pull_requests" not in result

    def test_created_at_resolver(self):
        """Test created_at resolver uses idx_created_at."""
        from unittest.mock import Mock

        mock_chapter = Mock()
        mock_chapter.idx_created_at = 1672531200

        field = self._get_field_by_name("created_at", ChapterNode)
        result = field.base_resolver.wrapped_func(None, mock_chapter)

        assert result == 1672531200

    def test_geo_location_resolver_with_coordinates(self):
        """Test geo_location resolver with valid coordinates."""
        from unittest.mock import Mock

        from apps.owasp.api.internal.nodes.chapter import GeoLocationType

        mock_chapter = Mock()
        mock_chapter.latitude = 40.7128
        mock_chapter.longitude = -74.0060

        field = self._get_field_by_name("geo_location", ChapterNode)
        result = field.base_resolver.wrapped_func(None, mock_chapter)

        assert isinstance(result, GeoLocationType)
        assert result.lat == 40.7128
        assert result.lng == -74.0060

    def test_geo_location_resolver_without_coordinates(self):
        """Test geo_location resolver returns None without coordinates."""
        from unittest.mock import Mock

        mock_chapter = Mock()
        mock_chapter.latitude = None
        mock_chapter.longitude = None

        field = self._get_field_by_name("geo_location", ChapterNode)
        result = field.base_resolver.wrapped_func(None, mock_chapter)

        assert result is None

    def test_key_resolver(self):
        """Test key resolver uses idx_key."""
        from unittest.mock import Mock

        mock_chapter = Mock()
        mock_chapter.idx_key = "www-chapter-test"

        field = self._get_field_by_name("key", ChapterNode)
        result = field.base_resolver.wrapped_func(None, mock_chapter)

        assert result == "www-chapter-test"

    def test_suggested_location_resolver(self):
        """Test suggested_location resolver uses idx_suggested_location."""
        from unittest.mock import Mock

        mock_chapter = Mock()
        mock_chapter.idx_suggested_location = "New York, USA"

        field = self._get_field_by_name("suggested_location", ChapterNode)
        result = field.base_resolver.wrapped_func(None, mock_chapter)

        assert result == "New York, USA"

    def test_suggested_location_resolver_none(self):
        """Test suggested_location resolver when None."""
        from unittest.mock import Mock

        mock_chapter = Mock()
        mock_chapter.idx_suggested_location = None

        field = self._get_field_by_name("suggested_location", ChapterNode)
        result = field.base_resolver.wrapped_func(None, mock_chapter)

        assert result is None
