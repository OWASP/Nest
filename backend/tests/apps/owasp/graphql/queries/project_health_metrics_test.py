"""Test Cases for Project Health Metrics GraphQL Queries."""

from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.owasp.graphql.nodes.health_stats import HealthStatsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


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

        assert health_stats_field.type.of_type is HealthStatsNode

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects")
    def test_resolve_health_stats(self, mock_metrics_objects):
        """Test resolving the health stats."""
        mock_metrics = [
            MagicMock(
                spec=ProjectHealthMetrics,
                score=85.0,
                stars_count=1000,
                forks_count=200,
                contributors_count=50,
                nest_created_at=timezone.make_aware(timezone.datetime(2025, 1, 1), timezone.get_default_timezone()),
                project=MagicMock(
                    name="Healthy Project",
                ),
            ),
            MagicMock(
                spec=ProjectHealthMetrics,
                score=70.0,
                stars_count=1500,
                forks_count=300,
                contributors_count=75,
                nest_created_at=timezone.make_aware(timezone.datetime(2025, 1, 2), timezone.get_default_timezone()),
                project=MagicMock(
                    name="Project Needing Attention",
                ),
            ),
            MagicMock(
                spec=ProjectHealthMetrics,
                score=60.0,
                stars_count=1200,
                forks_count=250,
                contributors_count=60,
                nest_created_at=timezone.make_aware(timezone.datetime(2025, 2, 3), timezone.get_default_timezone()),
                project=MagicMock(
                    name="Another Project Needing Attention",
                ),
            ),
            MagicMock(
                spec=ProjectHealthMetrics,
                score=40.0,
                stars_count=800,
                forks_count=150,
                contributors_count=30,
                nest_created_at=timezone.make_aware(timezone.datetime(2025, 3, 4), timezone.get_default_timezone()),
                project=MagicMock(
                    name="Unhealthy Project",
                ),
            ),
        ]
        mock_metrics_objects.return_value.values.return_value.order_by.return_value.distinct.return_value = mock_metrics
        query = ProjectHealthMetricsQuery()
        result = query.health_stats()
        assert isinstance(result, HealthStatsNode)
        assert result.healthy_projects_count == 1
        assert result.projects_needing_attention_count == 2
        assert result.unhealthy_projects_count == 1
        assert result.average_score == sum(m.score for m in mock_metrics) / len(mock_metrics)
        assert result.total_stars == sum(m.stars_count for m in mock_metrics)
        assert result.total_forks == sum(m.forks_count for m in mock_metrics)
        assert result.total_contributors == sum(m.contributors_count for m in mock_metrics)
        assert result.monthly_overall_scores == [
            (85.0 + 70.0) / 2,
            60.0,
            40.0,
        ]
