"""OWASP Project Health Metrics Node."""

import strawberry
import strawberry_django

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry_django.type(
    ProjectHealthMetrics,
    fields=[
        "age_days",
        "contributors_count",
        "forks_count",
        "is_funding_requirements_compliant",
        "is_project_leaders_requirements_compliant",
        "last_commit_days",
        "last_pull_request_days",
        "last_release_days",
        "open_issues_count",
        "owasp_page_last_update_days",
        "recent_releases_count",
        "score",
        "stars_count",
        "unanswered_issues_count",
        "unassigned_issues_count",
    ],
)
class ProjectHealthMetricsNode:
    """Project health metrics node."""

    @strawberry.field
    def project_name(self) -> str:
        """Resolve project node."""
        return self.project.name
