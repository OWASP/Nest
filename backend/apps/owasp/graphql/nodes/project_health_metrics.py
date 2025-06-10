"""OWASP Project Health Metrics Node."""

import strawberry

from apps.owasp.graphql.nodes.project import ProjectNode


@strawberry.type
class ProjectHealthMetricsNode:
    """Project health metrics node."""

    age_days: int = strawberry.field(description="Project age in days")
    contributors_count: int = strawberry.field(description="Number of contributors")
    last_commit_days: int = strawberry.field(description="Days since last commit")
    last_pull_request_days: int = strawberry.field(description="Days since last pull request")
    last_release_days: int = strawberry.field(description="Days since last release")
    recent_issues_count: int = strawberry.field(description="Recent issues count")
    recent_pull_requests_count: int = strawberry.field(description="Recent pull requests count")
    recent_releases_count: int = strawberry.field(description="Recent releases count")
    score: float = strawberry.field(description="Project health score (0-100)")
    forks_count: int = strawberry.field(description="Number of forks")
    stars_count: int = strawberry.field(description="Number of stars")
    is_project_leaders_requirements_compliant: bool = strawberry.field(
        description="Is leaders requirement compliant"
    )
    is_funding_requirements_compliant: bool = strawberry.field(
        description="Is funding policy requirements compliant"
    )
    open_issues_count: int = strawberry.field(description="Open issues count")
    unanswered_issues_count: int = strawberry.field(description="Unanswered issues count")

    @strawberry.field
    def project(self) -> ProjectNode:
        """Resolve project node."""
        return self.project
