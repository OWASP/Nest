from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


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
            "is_contributors_requirement_compliant",
            "is_funding_requirements_compliant",
            "has_no_recent_commits",
            "has_recent_releases",
            "is_leader_requirements_compliant",
            "limit",
            "has_long_open_issues",
            "has_long_unanswered_issues",
            "has_long_unassigned_issues",
            "has_low_score",
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

    def test_resolve_unhealthy_projects_without_filters(self):
        """Test the resolution of unhealthy projects."""
        # MagicMock the queryset
        mock_queryset = MagicMock()
        self.mocked_objects.select_related.return_value = mock_queryset
        mock_queryset.order_by.return_value.distinct.return_value = mock_queryset
        # Filters
        mock_filter = MagicMock()
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

    def test_resolve_unhealthy_projects_with_filters(self):
        """Test the resolution of unhealthy projects with filters."""
        # MagicMock the queryset
        mock_queryset = MagicMock()
        mock_metrics = MagicMock(spec=ProjectHealthMetrics)
        mock_metrics.project = MagicMock(spec=Project)
        mock_metrics.project.key = "test_project_key"
        mock_metrics.nest_created_at = "2023-10-01T00:00:00Z"
        mock_metrics.score = 45.0
        mock_metrics.contributors_count = 3
        mock_metrics.is_funding_requirements_compliant = False
        mock_metrics.is_leader_requirements_compliant = True
        mock_metrics.has_no_recent_commits = True
        mock_metrics.has_long_open_issues = True
        mock_metrics.has_long_unanswered_issues = True
        mock_metrics.has_long_unassigned_issues = True
        mock_metrics.recent_releases_count = 2

        mock_metrics_filtered_same_project = MagicMock(spec=ProjectHealthMetrics)
        mock_metrics_filtered_same_project.project = mock_metrics.project
        mock_metrics_filtered_same_project.nest_created_at = "2023-09-01T00:00:00Z"

        mock_metrics_filtered_different_project = MagicMock(spec=ProjectHealthMetrics)
        mock_metrics_filtered_different_project.project = MagicMock(spec=Project)
        mock_metrics_filtered_different_project.project.key = "different_project_key"
        mock_metrics_filtered_different_project.has_recent_commits = False

        self.mocked_objects.select_related.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(
            [
                mock_metrics,
                mock_metrics_filtered_same_project,
                mock_metrics_filtered_different_project,
            ]
        )
        mock_queryset.order_by.return_value.distinct.return_value = mock_queryset

        # Filters
        mock_filter = MagicMock()
        mock_queryset.filter.return_value = mock_filter
        mock_filter.select_related.return_value = [mock_metrics]

        # Create an instance of the query class
        query_instance = ProjectHealthMetricsQuery()

        # Call the method with filters
        result = query_instance.unhealthy_projects(
            is_contributors_requirement_compliant=True,
            is_funding_requirements_compliant=False,
            has_no_recent_commits=True,
            has_recent_releases=True,
            is_leader_requirements_compliant=True,
            limit=10,
            has_long_open_issues=True,
            has_long_unanswered_issues=True,
            has_long_unassigned_issues=True,
            has_low_score=True,
        )

        # Assert that the mocked queryset was called correctly with filters
        self.mocked_objects.select_related.assert_called_with("project")
        mock_queryset.order_by.assert_called_with("project__key", "-nest_created_at")
        mock_queryset.filter.assert_called_with(
            contributors_count__gte=2,
            has_no_recent_commits=True,
            has_long_open_issues=True,
            has_long_unanswered_issues=True,
            has_long_unassigned_issues=True,
            is_funding_requirements_compliant=False,
            is_leader_requirements_compliant=True,
            recent_releases_count__gt=0,
            score__lt=50,
        )
        mock_filter.select_related.assert_called_with("project")
        assert len(result) == 1
        assert result[0].project.key == "test_project_key"
        assert result[0].score == mock_metrics.score
        assert result[0].contributors_count == mock_metrics.contributors_count
