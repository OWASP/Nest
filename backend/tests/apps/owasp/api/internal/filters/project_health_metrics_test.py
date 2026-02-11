"""Test cases for the ProjectHealthMetricsFilter."""

from apps.owasp.api.internal.filters.project_health_metrics import ProjectHealthMetricsFilter
from apps.owasp.models.enums.project import ProjectLevel


class TestProjectHealthMetricsFilter:
    """Test cases for ProjectHealthMetricsFilter class."""

    def test_filter_has_strawberry_definition(self):
        """Check if ProjectHealthMetricsFilter has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsFilter, "__strawberry_definition__")

    def test_filter_fields(self):
        """Test if the filter fields are correctly defined."""
        filter_fields = {
            field.name for field in ProjectHealthMetricsFilter.__strawberry_definition__.fields
        }
        expected_fields = {"score", "level"}
        assert expected_fields.issubset(filter_fields)

    def test_filtering(self):
        """Test filtering by project level and score."""
        filter_instance = ProjectHealthMetricsFilter(level="flagship", score=50)
        assert filter_instance.level == ProjectLevel.FLAGSHIP
        assert filter_instance.score == 50

    def test_level_filter_with_none_value(self):
        """Test level filter returns empty Q() when value is None."""
        from django.db.models import Q

        # Get the filter method from the Strawberry definition
        level_field = None
        for field in ProjectHealthMetricsFilter.__strawberry_definition__.fields:
            if field.name == "level":
                level_field = field
                break

        assert level_field is not None

        # Access the wrapped function and call it with self, value, and prefix
        filter_instance = ProjectHealthMetricsFilter()
        result = level_field.base_resolver.wrapped_func(filter_instance, value=None, prefix="")

        # Empty Q() should be returned when value is None
        assert result == Q()
        assert result.children == []
