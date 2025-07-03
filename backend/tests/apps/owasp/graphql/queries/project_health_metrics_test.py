"""Test Cases for Project Health Metrics GraphQL Queries."""

from unittest.mock import patch

from apps.owasp.graphql.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery


class TestProjectHealthMetricsQuery:
    """Test cases for ProjectHealthMetricsQuery class."""

    def test_health_stats_query_has_strawberry_definition(self):
        """Check if ProjectHealthMetricsQuery has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsQuery, "__strawberry_definition__")

        field_names = {
            field.name for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
        }
        assert "project_health_stats" in field_names

    def test_health_stats_field_configuration(self):
        """Test if 'project_health_stats' field is configured properly."""
        health_stats_field = next(
            field
            for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
            if field.name == "project_health_stats"
        )

        assert health_stats_field.type is ProjectHealthStatsNode

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_stats")
    def test_resolve_health_stats(self, mock_get_stats):
        """Test resolving the health stats."""
        expected_stats = ProjectHealthStatsNode(
            average_score=65.0,
            monthly_overall_scores=[77.5, 60.0, 40.0],
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
