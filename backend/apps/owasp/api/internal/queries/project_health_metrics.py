"""OWASP Project Health Metrics Queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.filters.project_health_metrics import ProjectHealthMetricsFilter
from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.api.internal.ordering.project_health_metrics import ProjectHealthMetricsOrder
from apps.owasp.api.internal.permissions.project_health_metrics import HasDashboardAccess
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry.type
class ProjectHealthMetricsQuery:
    """Project health metrics queries."""

    @strawberry_django.field(
        filters=ProjectHealthMetricsFilter,
        description="List of project health metrics.",
        pagination=True,
        ordering=ProjectHealthMetricsOrder,
        permission_classes=[HasDashboardAccess],
    )
    def project_health_metrics(
        self,
        filters: ProjectHealthMetricsFilter | None = None,
        pagination: strawberry_django.pagination.OffsetPaginationInput | None = None,
        ordering: list[ProjectHealthMetricsOrder] | None = None,
    ) -> list[ProjectHealthMetricsNode]:
        """Resolve project health metrics based on filters, pagination, and ordering.

        Args:
            filters (ProjectHealthMetricsFilter): Filters to apply on the metrics.
            pagination (strawberry_django.pagination.OffsetPaginationInput): Pagination parameters.
            ordering (list[ProjectHealthMetricsOrder], optional): Ordering parameters.

        Returns:
            list[ProjectHealthMetricsNode]: List of project health metrics.

        """
        return ProjectHealthMetrics.get_latest_health_metrics()

    @strawberry.field(
        permission_classes=[HasDashboardAccess],
    )
    def project_health_stats(self) -> ProjectHealthStatsNode:
        """Resolve overall project health stats.

        Returns:
            ProjectHealthStatsNode: The overall health stats of all projects.

        """
        return ProjectHealthMetrics.get_stats()

    @strawberry.field(
        permission_classes=[HasDashboardAccess],
    )
    def project_health_metrics_distinct_length(
        self,
        filters: ProjectHealthMetricsFilter | None = None,
    ) -> int:
        """Get the distinct length of project health metrics.

        Args:
            filters (ProjectHealthMetricsFilter | None): Filters to apply on the metrics.

        Returns:
            int: The count of distinct project health metrics.

        """
        queryset = ProjectHealthMetrics.get_latest_health_metrics()

        if filters:
            queryset = strawberry_django.filters.apply(filters, queryset)

        return queryset.count()
