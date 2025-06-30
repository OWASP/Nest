"""OWASP Project Health Metrics Queries."""

import strawberry

from apps.owasp.graphql.nodes.health_stats import HealthStatsNode
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry.type
class ProjectHealthMetricsQuery:
    """Project health metrics queries."""

    @strawberry.field
    def health_stats(self) -> HealthStatsNode:
        """Resolve overall project health stats.

        Returns:
            HealthStatsNode: The overall health stats of all projects.

        """
        return ProjectHealthMetrics.get_overall_stats()
