"""OWASP Project Health Metrics Ordering."""

import strawberry
from strawberry_django import order_type

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@order_type(ProjectHealthMetrics)
class ProjectHealthMetricsOrder:
    """Ordering for Project Health Metrics."""

    score: strawberry.auto

    # We need to order by another field in case of equal scores
    # to ensure unique metrics in pagination.
    # The ORM returns random ordered query set if no order is specified.
    # We don't do ordering in the model since we order already in the query.
    project__name: strawberry.auto
