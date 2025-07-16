"""OWASP Project Health Metrics Ordering."""

from strawberry import auto
from strawberry_django import order_type

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@order_type(ProjectHealthMetrics)
class ProjectHealthMetricsOrder:
    """Ordering for Project Health Metrics."""

    score: auto
