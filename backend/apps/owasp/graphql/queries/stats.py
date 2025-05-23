"""OWASP stats GraphQL queries."""

from math import floor

import graphene

from apps.github.models.user import User
from apps.owasp.graphql.nodes.stats import StatsNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project
from apps.slack.models.workspace import Workspace

# Used as a minimum threshold for rounding down stats
# to avoid rounding down to zero
MINROUNDED = 10


class StatsQuery:
    """Stats queries."""

    stats_overview = graphene.Field(StatsNode)

    @staticmethod
    def general_round_down(stats: int, base: int) -> int:
        """Round down the stats to the nearest base.

        Args:
            stats: The stats to round down.
            base: The base to round down to.

        Returns:
            int: The rounded down stats.

        """
        if stats == 0 or stats <= MINROUNDED:
            return stats
        return floor(stats / base) * base

    def resolve_stats_overview(self, info) -> StatsNode:
        """Resolve stats overview.

        Args:
            self: The StatsQuery instance.
            info: GraphQL execution info.

        Returns:
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
        workspace = Workspace.objects.first()
        workspace_stats = workspace.total_members_count if workspace else 0

        return StatsNode(
            active_projects_stats=StatsQuery.general_round_down(active_projects_stats, 10),
            active_chapters_stats=StatsQuery.general_round_down(active_chapters_stats, 10),
            contributors_stats=StatsQuery.general_round_down(contributors_stats, 100),
            countries_stats=StatsQuery.general_round_down(countries_stats, 10),
            workspace_stats=StatsQuery.general_round_down(workspace_stats, 100),
        )
