from unittest.mock import Mock, patch

from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class ProjectHealthMetricsQueryTest:
    """Test cases for ProjectHealthMetricsQuery class."""

    def test_project_health_metrics_query_has_strawberry_definition(self):
        """Check if ProjectHealthMetricsQuery has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsQuery, "__strawberry_definition__")

        field_names = [
            field.name for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
        ]
        assert "project_health_metrics" in field_names

    def test_project_health_metrics_field_configuration(self):
        """Test if 'project_health_metrics' field is configured properly."""
        health_metrics_field = next(
            field
            for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
            if field.name == "project_health_metrics"
        )

        assert health_metrics_field.type.of_type is ProjectHealthMetricsNode

        arg_names = [arg.python_name for arg in health_metrics_field.arguments]
        assert "key" in arg_names

        key_arg = next(arg for arg in health_metrics_field.arguments if arg.python_name == "key")
        assert key_arg.type_annotation.annotation is str


class ProjectHealthMetricsResolutionTest:
    """Test cases for resolving the project_health_metrics field."""

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects")
    def test_resolve_unhealthy_projects(self, mocked_objects):
        """Test the resolution of unhealthy projects."""
        # Mock the queryset
        mock_queryset = Mock(spec=ProjectHealthMetrics.objects)
        mocked_objects.select_related.return_value.order_by.return_value = mock_queryset

        # Create a mock instance of ProjectHealthMetricsNode
        mock_node = Mock(spec=ProjectHealthMetricsNode)
        mock_queryset.all.return_value = [mock_node]

        # Create an instance of the query class
        query_instance = ProjectHealthMetricsQuery()

        # Call the method
        result = query_instance.unhealthy_projects()

        # Assert that the mocked queryset was called correctly
        mocked_objects.select_related.assert_called_with("project")
        mocked_objects.select_related.return_value.order_by.assert_called_with(
            "project__key", "-nest_created_at", "-score"
        )

        # Assert that the result is as expected
        assert result == [mock_node]
