"""Test Cases for Project Health Metrics GraphQL Queries."""

from unittest.mock import patch

from apps.owasp.graphql.nodes.health_stats import HealthStatsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery


class TestProjectHealthMetricsQuery:
    """Test cases for ProjectHealthMetricsQuery class."""

    def test_health_stats_query_has_strawberry_definition(self):
        """Check if ProjectHealthMetricsQuery has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsQuery, "__strawberry_definition__")

        field_names = [
            field.name for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
        ]
        assert "health_stats" in field_names

    def test_health_stats_field_configuration(self):
        """Test if 'health_stats' field is configured properly."""
        health_stats_field = next(
            field
            for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
            if field.name == "health_stats"
        )

        assert health_stats_field.type is HealthStatsNode

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_overall_stats")
    def test_resolve_health_stats(self, mock_get_overall_stats):
        """Test resolving the health stats."""
        expected_stats = HealthStatsNode(
            healthy_projects_count=1,
            healthy_projects_percentage=25.0,
            projects_needing_attention_count=2,
            projects_needing_attention_percentage=50.0,
            unhealthy_projects_count=1,
            unhealthy_projects_percentage=25.0,
            average_score=65.0,
            total_stars=4500,
            total_forks=900,
            total_contributors=215,
            monthly_overall_scores=[77.5, 60.0, 40.0],
        )
        mock_get_overall_stats.return_value = expected_stats

        query = ProjectHealthMetricsQuery()
        result = query.health_stats()
        mock_get_overall_stats.assert_called_once()
        assert result == expected_stats
