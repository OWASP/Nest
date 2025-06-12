from unittest.mock import Mock, patch

import pytest

from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery


class TestProjectHealthMetricsQuery:
    """Test cases for ProjectHealthMetricsQuery class."""

    def test_unhealthy_projects_query_has_strawberry_definition(self):
        """Check if ProjectHealthMetricsQuery has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsQuery, "__strawberry_definition__")

        field_names = [
            field.name for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
        ]
        assert "unhealthy_projects" in field_names

    def test_unhealthy_projects_field_configuration(self):
        """Test if 'unhealthy_projects' field is configured properly."""
        unhealthy_projects_field = next(
            field
            for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
            if field.name == "unhealthy_projects"
        )

        assert unhealthy_projects_field.type.of_type is ProjectHealthMetricsNode

        arg_names = [arg.python_name for arg in unhealthy_projects_field.arguments]
        expected_arg_names = [
            "contributors_count_requirement_compliant",
            "funding_requirement_compliant",
            "no_recent_commits",
            "no_recent_releases",
            "leaders_requirement_compliant",
            "limit",
            "long_open_issues",
            "long_unanswered_issues",
            "long_unassigned_issues",
            "low_score",
        ]
        assert set(arg_names) == set(expected_arg_names)


class TestProjectHealthMetricsResolution:
    """Test cases for resolving the unhealthy_projects field."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        with patch(
            "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects"
        ) as mocked_objects:
            self.mocked_objects = mocked_objects
            yield

    def test_resolve_unhealthy_projects(self):
        """Test the resolution of unhealthy projects."""
        # Mock the queryset
        mock_queryset = Mock()
        self.mocked_objects.select_related.return_value = mock_queryset
        mock_queryset.order_by.return_value.distinct.return_value = mock_queryset
        # Filters
        mock_filter = Mock()
        mock_queryset.filter.return_value = mock_filter
        mock_filter.select_related.return_value = [mock_filter]
        # Create an instance of the query class
        query_instance = ProjectHealthMetricsQuery()

        # Call the method
        result = query_instance.unhealthy_projects()

        # Assert that the mocked queryset was called correctly
        self.mocked_objects.select_related.assert_called_with("project")
        mock_queryset.order_by.assert_called_with("project__key", "-nest_created_at")

        assert isinstance(result, list)
        mock_filter.select_related.assert_called_with("project")
