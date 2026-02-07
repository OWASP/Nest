"""Test Cases for Project Health Metrics GraphQL Queries."""

from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.api.internal.queries.project_health_metrics import (
    MAX_LIMIT,
    MAX_OFFSET,
    ProjectHealthMetricsQuery,
)


class TestProjectHealthMetricsQuery:
    """Test cases for ProjectHealthMetricsQuery class."""

    @pytest.mark.parametrize(
        "field_name",
        [
            "project_health_stats",
            "project_health_metrics",
        ],
    )
    def test_field_query_has_strawberry_definition(self, field_name):
        """Check if ProjectHealthMetricsQuery has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsQuery, "__strawberry_definition__")

        field_names = {
            field.name for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
        }
        assert field_name in field_names

    @pytest.mark.parametrize(
        ("field_name", "expected_type"),
        [
            ("project_health_metrics", ProjectHealthMetricsNode),
            ("project_health_stats", ProjectHealthStatsNode),
        ],
    )
    def test_field_configuration(self, field_name, expected_type):
        """Test if the field has the correct type in Strawberry definition."""
        query_field = next(
            field
            for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
            if field.name == field_name
        )

        assert query_field.type is expected_type or query_field.type.of_type is expected_type

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_stats")
    def test_resolve_health_stats(self, mock_get_stats):
        """Test resolving the health stats."""
        expected_stats = ProjectHealthStatsNode(
            average_score=65.0,
            monthly_overall_scores=[77.5, 60, 40],
            monthly_overall_scores_months=[1, 2, 3],
            projects_count_healthy=1,
            projects_count_need_attention=2,
            projects_count_unhealthy=1,
            projects_percentage_healthy=25.0,
            projects_percentage_need_attention=50.0,
            projects_percentage_unhealthy=25.0,
            total_contributors=215,
            total_forks=900,
            total_stars=4500,
        )
        mock_get_stats.return_value = expected_stats

        query = ProjectHealthMetricsQuery()
        result = query.project_health_stats()
        mock_get_stats.assert_called_once()
        assert result == expected_stats

    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics"
    )
    def test_resolve_project_health_metrics(self, mock_get_latest_metrics):
        """Test resolving project health metrics."""
        metrics = [
            ProjectHealthMetricsNode(
                stars_count=1000,
                forks_count=200,
                score=85,
                contributors_count=50,
                open_issues_count=10,
                open_pull_requests_count=5,
                unanswered_issues_count=2,
                unassigned_issues_count=1,
                is_funding_requirements_compliant=True,
                is_leader_requirements_compliant=True,
                recent_releases_count=3,
                total_issues_count=15,
                total_releases_count=5,
            )
        ]
        mock_get_latest_metrics.return_value = metrics
        query = ProjectHealthMetricsQuery()
        result = query.project_health_metrics(filters=None, pagination=None, ordering=None)
        assert isinstance(result, list)
        assert isinstance(result[0], ProjectHealthMetricsNode)
        assert len(result) == 1
        assert result[0].stars_count == 1000
        assert result[0].forks_count == 200

    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics"
    )
    def test_project_health_metrics_distinct_length(self, mock_get_latest_metrics):
        """Test the distinct length of project health metrics."""
        mock_get_latest_metrics.return_value.count.return_value = 42
        query = ProjectHealthMetricsQuery()
        result = query.project_health_metrics_distinct_length()
        assert result == 42
        mock_get_latest_metrics.return_value.count.assert_called_once()


class TestProjectHealthMetricsPagination:
    """Test cases for pagination edge cases in ProjectHealthMetricsQuery."""

    def test_project_health_metrics_negative_offset_returns_empty(self):
        """Test that negative offset returns empty list."""
        query = ProjectHealthMetricsQuery()
        pagination = MagicMock()
        pagination.offset = -1
        pagination.limit = 10

        result = query.project_health_metrics(pagination=pagination)
        assert result == []

    def test_project_health_metrics_zero_limit_returns_empty(self):
        """Test that zero limit returns empty list."""
        query = ProjectHealthMetricsQuery()
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = 0

        result = query.project_health_metrics(pagination=pagination)
        assert result == []

    def test_project_health_metrics_negative_limit_returns_empty(self):
        """Test that negative limit returns empty list."""
        query = ProjectHealthMetricsQuery()
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = -5

        result = query.project_health_metrics(pagination=pagination)
        assert result == []

    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics"
    )
    def test_project_health_metrics_offset_clamped_to_max(self, mock_get_latest_metrics):
        """Test that offset is clamped to MAX_OFFSET."""
        query = ProjectHealthMetricsQuery()
        pagination = MagicMock()
        pagination.offset = 50000
        pagination.limit = None

        mock_get_latest_metrics.return_value = []
        query.project_health_metrics(pagination=pagination)

        assert pagination.offset == MAX_OFFSET

    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics"
    )
    def test_project_health_metrics_limit_clamped_to_max(self, mock_get_latest_metrics):
        """Test that limit is clamped to MAX_LIMIT."""
        query = ProjectHealthMetricsQuery()
        pagination = MagicMock()
        pagination.offset = 0
        pagination.limit = 5000

        mock_get_latest_metrics.return_value = []
        query.project_health_metrics(pagination=pagination)

        assert pagination.limit == MAX_LIMIT

    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics"
    )
    @patch("strawberry_django.filters.apply")
    def test_project_health_metrics_distinct_length_with_filters(
        self, mock_apply, mock_get_latest_metrics
    ):
        """Test distinct_length with filters applied."""
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 10
        mock_get_latest_metrics.return_value = mock_queryset
        mock_apply.return_value = mock_queryset

        mock_filters = MagicMock()
        query = ProjectHealthMetricsQuery()
        result = query.project_health_metrics_distinct_length(filters=mock_filters)

        assert result == 10
        mock_apply.assert_called_once_with(mock_filters, mock_queryset)
