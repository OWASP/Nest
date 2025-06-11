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
        # Set the default of the `funding_requirement_compliant`
        # `leaders_requirement_compliant`, `long_open_issues`, `long_unanswered_issues`,
        # `contributors_count_requirement_compliant`,
        # and `long_unassigned_issues` parameters to None,
        # to allow retrieving projects with or without these requirements
        contributors_count_requirement_compliant: bool | None = None,
        funding_requirement_compliant: bool | None = None,
        no_recent_commits: bool | None = None,
        no_recent_releases: bool = False,
        leaders_requirement_compliant: bool | None = None,
        limit: int = 20,
        long_open_issues: bool | None = None,
        long_unanswered_issues: bool | None = None,
        long_unassigned_issues: bool | None = None,
        # Because the default behavior is to return unhealthy projects with low scores,
        # we set `low_score` to True by default.
        # We may return projects with high scores to indicate issues that need attention,
        # like a lack of contributors, recent commits, or otherwise.
        # We set the default of other parameters to False,
        # to allow retrieving all unhealthy projects without any filters.
        low_score: bool = True,
    ) -> list[ProjectHealthMetricsNode]:
        """Resolve unhealthy projects."""
        filters = {}

        if no_recent_releases:
            filters["recent_releases_count"] = 0

        if contributors_count_requirement_compliant is not None:
            filters["contributors_count__lt"] = CONTRIBUTORS_COUNT_REQUIREMENT

        if no_recent_commits is not None:
            filters["has_no_recent_commits"] = no_recent_commits

        if long_open_issues is not None:
            filters["has_long_open_issues"] = long_open_issues

        if long_unanswered_issues is not None:
            filters["has_long_unanswered_issues"] = long_unanswered_issues

        if long_unassigned_issues is not None:
            filters["has_long_unassigned_issues"] = long_unassigned_issues

        if leaders_requirement_compliant is not None:
            filters["is_project_leaders_requirements_compliant"] = leaders_requirement_compliant

        if funding_requirement_compliant is not None:
            filters["is_funding_requirements_compliant"] = funding_requirement_compliant

        if low_score:
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
