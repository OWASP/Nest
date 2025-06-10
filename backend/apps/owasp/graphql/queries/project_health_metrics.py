"""OWASP Project Health Metrics Queries."""

import strawberry
from django.utils import timezone

from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

# It is stated in issue #711
CONTRIBUTORS_COUNT_REQUIREMENT = 2

# These numbers are just for testing purposes, they can be adjusted later
OPEN_ISSUES_LIMIT = 40
LONG_UNANSWERED_ISSUES_LIMIT = 30
LONG_UNASSIGNED_ISSUES_LIMIT = 30


@strawberry.type
class ProjectHealthMetricsQuery:
    """Project health metrics queries."""

    @strawberry.field
    def unhealthy_projects(
        self,
        *,
        contributors_count_requirement_compliant: bool = True,
        funding_requirement_compliant: bool = True,
        no_recent_commits: bool = False,
        no_recent_releases: bool = False,
        leaders_requirement_compliant: bool = True,
        long_open_issues: bool = False,
        long_unanswered_issues: bool = False,
        long_unassigned_issues: bool = False,
        low_score: bool = False,
    ) -> list[ProjectHealthMetricsNode]:
        """Resolve unhealthy projects."""
        filters = {}

        if not contributors_count_requirement_compliant:
            filters["contributors_count__lt"] = CONTRIBUTORS_COUNT_REQUIREMENT

        if no_recent_releases:
            filters["recent_releases_count"] = 0

        if long_open_issues:
            filters["open_issues_count__gt"] = OPEN_ISSUES_LIMIT

        if long_unanswered_issues:
            filters["unanswered_issues_count__gt"] = LONG_UNANSWERED_ISSUES_LIMIT

        if long_unassigned_issues:
            filters["unassigned_issues_count__gt"] = LONG_UNASSIGNED_ISSUES_LIMIT

        if low_score:
            filters["score__lt"] = 50

        filters["is_project_leaders_requirements_compliant"] = leaders_requirement_compliant

        filters["is_funding_requirements_compliant"] = funding_requirement_compliant

        # Get the last created metrics (one for each project)
        queryset = (
            ProjectHealthMetrics.objects.select_related("project")
            .order_by("project__key", "-created_at")
            .distinct("project__key")
        )

        # Apply filters
        if filters:
            queryset = queryset.filter(**filters)

        if no_recent_commits:
            from django.db.models import Q

            # Again, this is just for testing purposes, it can be adjusted later
            # Define a recent period (e.g., 120 days)
            recent_period = timezone.now() - timezone.timedelta(days=120)
            no_commits_filter = Q(last_committed_at__isnull=True) | Q(
                last_committed_at__lt=recent_period
            )
            queryset = queryset.filter(no_commits_filter)

        return queryset
