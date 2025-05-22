"""OWASP stats GraphQL queries."""

import strawberry

from apps.github.models.user import User
from apps.owasp.graphql.nodes.stats import StatsNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project


@strawberry.type
class StatsQuery:
    """Stats queries."""

    @strawberry.field
    def stats_overview(self) -> StatsNode:
        """Resolve stats overview."""
        active_projects_stats = Project.active_projects_count()
        active_chapters_stats = Chapter.active_chapters_count()
        contributors_stats = User.objects.count()
        countries_stats = (
            Chapter.objects.filter(country__isnull=False)
            .exclude(country="")
            .values("country")
            .distinct()
            .count()
        )

        return StatsNode(
            active_projects_stats=(active_projects_stats // 10) * 10,
            active_chapters_stats=(active_chapters_stats // 10) * 10,
            contributors_stats=(contributors_stats // 100) * 100,
            countries_stats=(countries_stats // 10) * 10,
        )
