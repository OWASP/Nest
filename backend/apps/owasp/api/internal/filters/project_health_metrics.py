"""Filters for OWASP ProjectHealthMetrics."""

import strawberry
import strawberry_django
from django.db.models import Q

from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry_django.filter_type(ProjectHealthMetrics, lookups=True)
class ProjectHealthMetricsFilter:
    """Filter for ProjectHealthMetrics."""

    score: strawberry.auto

    @strawberry_django.filter_field
    # prefix is required for strawberry to work with nested filters
    # Q is the return type for the filter
    def level(self, value: str, prefix: str):
        """Filter by project level."""
        return (
            Q(project__level=ProjectLevel(value))
            if value and ProjectLevel.choices.__contains__(value)
            else Q()
        )
