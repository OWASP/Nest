"""OWASP stats GraphQL queries."""

import graphene

from apps.github.models.user import User
from apps.owasp.graphql.nodes.stats import StatsNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project


class StatsQuery:
    """Stats queries."""

    stats_overview = graphene.Field(StatsNode)

    def resolve_stats_overview(self, info, **kwargs):
        """Resolve stats overview.

        Args:
        ----
            self: The StatsQuery instance.
            info: GraphQL execution info.
            **kwargs: Additional arguments.

        Returns:
        -------
            StatsNode: A node containing aggregated statistics.

        """
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

        active_projects_stats = (active_projects_stats // 10) * 10  # nearest 10
        active_chapters_stats = (active_chapters_stats // 10) * 10
        contributors_stats = (contributors_stats // 100) * 100  # nearest 100
        countries_stats = (countries_stats // 10) * 10

        return StatsNode(
            active_projects_stats,
            active_chapters_stats,
            contributors_stats,
            countries_stats,
        )
