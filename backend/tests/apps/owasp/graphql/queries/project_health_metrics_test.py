"""Test Cases for Project Health Metrics GraphQL Queries."""

from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.owasp.graphql.nodes.health_stats import HealthStatsNode
from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.graphql.queries.project_health_metrics import ProjectHealthMetricsQuery


class TestProjectHealthMetricsQuery:
    """Test cases for ProjectHealthMetricsQuery class."""

    @pytest.mark.parametrize(
        "field_name",
        [
            "health_stats",
            "project_health_metrics",
        ],
    )
    def test_field_query_has_strawberry_definition(self, field_name):
        """Check if ProjectHealthMetricsQuery has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsQuery, "__strawberry_definition__")

        field_names = [
            field.name for field in ProjectHealthMetricsQuery.__strawberry_definition__.fields
        ]
        assert field_name in field_names

    @pytest.mark.parametrize(
        ("field_name", "expected_type"),
        [
            ("project_health_metrics", ProjectHealthMetricsNode),
            ("health_stats", HealthStatsNode),
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

    def test_resolve_project_health_metrics(self):
        """Test resolving project health metrics."""
        metrics = [
            ProjectHealthMetrics(
                score=85.0,
                stars_count=1000,
                forks_count=200,
            )
        ]
        query = ProjectHealthMetricsQuery(project_health_metrics=metrics)
        result = query.project_health_metrics
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].stars_count == 1000
        assert result[0].score == 85.0
