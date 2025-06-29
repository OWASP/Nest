"""OWASP Project Health Metrics Queries."""

import strawberry
import strawberry_django

from apps.owasp.graphql.filters.project_health_metrics import ProjectHealthMetricsFilter
from apps.owasp.graphql.nodes.health_stats import HealthStatsNode
from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry.type
class ProjectHealthMetricsQuery:
    """Project health metrics queries."""

    project_health_metrics: list[ProjectHealthMetricsNode] = strawberry_django.field(
        filters=ProjectHealthMetricsFilter,
        description="List of project health metrics.",
    )

    @strawberry.field
    def health_stats(self) -> HealthStatsNode:
        """Resolve overall project health stats.

        Returns:
            HealthStatsNode: The overall health stats of all projects.

        """
        return ProjectHealthMetrics.get_overall_stats()
