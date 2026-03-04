"""Test cases for the ProjectFilter."""

from django.db.models import Q

from apps.owasp.api.internal.filters.project import ProjectFilter
from apps.owasp.models.enums.project import ProjectType


class TestProjectFilter:
    """Test cases for ProjectFilter class."""

    def test_filter_has_strawberry_definition(self):
        """Check if ProjectFilter has valid Strawberry definition."""
        assert hasattr(ProjectFilter, "__strawberry_definition__")

    def test_filter_fields(self):
        """Test if the filter fields are correctly defined."""
        filter_fields = {
            field.name for field in ProjectFilter.__strawberry_definition__.fields
        }
        assert "type" in filter_fields

    def test_type_filter_with_valid_value(self):
        """Test type filter returns Q object with condition when value is provided."""
        type_filter_method = ProjectFilter.__dict__["type"]
        result = type_filter_method(None, value=ProjectType.CODE, prefix="")

        assert isinstance(result, Q)
        assert result == Q(type=ProjectType.CODE)

    def test_type_filter_with_none_value(self):
        """Test type filter returns empty Q() when value is None."""
        type_filter_method = ProjectFilter.__dict__["type"]
        result = type_filter_method(None, value=None, prefix="")

        assert isinstance(result, Q)
        assert result == Q()

    def test_type_filter_with_different_types(self):
        """Test type filter works with various ProjectType values."""
        type_filter_method = ProjectFilter.__dict__["type"]

        for project_type in [ProjectType.CODE, ProjectType.DOCUMENTATION, ProjectType.TOOL]:
            result = type_filter_method(None, value=project_type, prefix="")
            assert result == Q(type=project_type)
            assert result == Q(type=project_type)
