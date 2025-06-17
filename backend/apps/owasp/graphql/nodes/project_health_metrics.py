"""OWASP Project Health Metrics Node."""

import strawberry
import strawberry_django

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@strawberry_django.type(
    ProjectHealthMetrics,
    fields=[
        "contributors_count",
        "forks_count",
        "is_funding_requirements_compliant",
        "is_leader_requirements_compliant",
        "open_issues_count",
        "open_pull_requests_count",
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
    def age_days(self) -> int:
        """Resolve project age in days."""
        return self.age_days

    @strawberry.field
    def last_commit_days(self) -> int:
        """Resolve last commit age in days."""
        return self.last_commit_days

    @strawberry.field
    def last_pull_request_days(self) -> int:
        """Resolve last pull request age in days."""
        return self.last_pull_request_days

    @strawberry.field
    def last_release_days(self) -> int:
        """Resolve last release age in days."""
        return self.last_release_days

    @strawberry.field
    def owasp_page_last_update_days(self) -> int:
        """Resolve OWASP page last update age in days."""
        return self.owasp_page_last_update_days
