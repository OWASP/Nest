"""OWASP Project Health Metrics Node."""

from datetime import datetime

import strawberry
import strawberry_django

from apps.owasp.api.internal.filters.project_health_metrics import ProjectHealthMetricsFilter
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
        "total_issues_count",
        "total_releases_count",
        "unanswered_issues_count",
        "unassigned_issues_count",
    ],
    filters=ProjectHealthMetricsFilter,
)
class ProjectHealthMetricsNode(strawberry.relay.Node):
    """Project health metrics node."""

    @strawberry_django.field
    def age_days(self) -> int:
        """Resolve project age in days."""
        return self.age_days

    @strawberry_django.field
    def age_days_requirement(self) -> int:
        """Resolve project age requirement in days."""
        return self.age_days_requirement

    @strawberry_django.field
    def created_at(self) -> datetime:
        """Resolve metrics creation date."""
        return self.nest_created_at

    @strawberry_django.field
    def last_commit_days(self) -> int:
        """Resolve last commit age in days."""
        return self.last_commit_days

    @strawberry_django.field
    def last_commit_days_requirement(self) -> int:
        """Resolve last commit age requirement in days."""
        return self.last_commit_days_requirement

    @strawberry_django.field
    def last_pull_request_days(self) -> int:
        """Resolve last pull request age in days."""
        return self.last_pull_request_days

    @strawberry_django.field
    def last_pull_request_days_requirement(self) -> int:
        """Resolve last pull request age requirement in days."""
        return self.last_pull_request_days_requirement

    @strawberry_django.field
    def last_release_days(self) -> int:
        """Resolve last release age in days."""
        return self.last_release_days

    @strawberry_django.field
    def last_release_days_requirement(self) -> int:
        """Resolve last release age requirement in days."""
        return self.last_release_days_requirement

    @strawberry_django.field
    def project_key(self) -> str:
        """Resolve project key."""
        return self.project.nest_key

    @strawberry_django.field
    def project_name(self) -> str:
        """Resolve project name."""
        return self.project.name

    @strawberry_django.field
    def owasp_page_last_update_days(self) -> int:
        """Resolve OWASP page last update age in days."""
        return self.owasp_page_last_update_days

    @strawberry_django.field
    def owasp_page_last_update_days_requirement(self) -> int:
        """Resolve OWASP page last update age requirement in days."""
        return self.owasp_page_last_update_days_requirement
