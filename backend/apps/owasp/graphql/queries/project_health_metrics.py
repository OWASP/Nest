"""OWASP Project Health Metrics Queries."""

import strawberry

from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

# It is stated in issue #711
CONTRIBUTORS_COUNT_REQUIREMENT = 2


@strawberry.type
class ProjectHealthMetricsQuery:
    """Project health metrics queries."""

    @strawberry.field
    def unhealthy_projects(
        self,
        *,
        is_contributors_requirement_compliant: bool | None = None,
        is_funding_requirements_compliant: bool | None = None,
        has_no_recent_commits: bool | None = None,
        has_recent_releases: bool | None = None,
        is_leader_requirements_compliant: bool | None = None,
        limit: int = 20,
        has_long_open_issues: bool | None = None,
        has_long_unanswered_issues: bool | None = None,
        has_long_unassigned_issues: bool | None = None,
        # Because the default behavior is to return unhealthy projects with low scores,
        # we set `low_score` to True by default.
        # We may return projects with high scores to indicate issues that need attention,
        # like a lack of contributors, recent commits, or otherwise.
        # We set the default of other parameters to None,
        # to allow retrieving all unhealthy projects without any filters.
        has_low_score: bool = True,
    ) -> list[ProjectHealthMetricsNode]:
        """Resolve unhealthy projects."""
        filters = {}

        if has_recent_releases is not None:
            if has_recent_releases:
                filters["recent_releases_count__gt"] = 0
            else:
                filters["recent_releases_count"] = 0

        if is_contributors_requirement_compliant is not None:
            suffix = "__gte" if is_contributors_requirement_compliant else "__lt"
            filters[f"contributors_count{suffix}"] = CONTRIBUTORS_COUNT_REQUIREMENT

        if has_no_recent_commits is not None:
            filters["has_no_recent_commits"] = has_no_recent_commits

        if has_long_open_issues is not None:
            filters["has_long_open_issues"] = has_long_open_issues

        if has_long_unanswered_issues is not None:
            filters["has_long_unanswered_issues"] = has_long_unanswered_issues

        if has_long_unassigned_issues is not None:
            filters["has_long_unassigned_issues"] = has_long_unassigned_issues

        if is_leader_requirements_compliant is not None:
            filters["is_leader_requirements_compliant"] = is_leader_requirements_compliant

        if is_funding_requirements_compliant is not None:
            filters["is_funding_requirements_compliant"] = is_funding_requirements_compliant

        if has_low_score:
            filters["score__lt"] = 50

        # Get the last created metrics (one for each project)
        queryset = (
            ProjectHealthMetrics.objects.select_related("project")
            .order_by("project__key", "-nest_created_at")
            .distinct("project__key")
        )

        # Apply filters
        if filters:
            queryset = queryset.filter(**filters)

        return queryset.select_related("project")[:limit]
