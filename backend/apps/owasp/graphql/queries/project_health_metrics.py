"""OWASP Project Health Metrics Queries."""

import strawberry

from apps.owasp.graphql.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry.type
class ProjectHealthMetricsQuery:
    """Project health metrics queries."""

    @strawberry.field
    def project_health_stats(self) -> ProjectHealthStatsNode:
        """Resolve overall project health stats.

        Returns:
            HealthStatsNode: The overall health stats of all projects.

        """
        return ProjectHealthMetrics.get_stats()
