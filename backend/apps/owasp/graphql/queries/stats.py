"""OWASP stats GraphQL queries."""

import graphene

from apps.common.utils import round_down
from apps.github.models.user import User
from apps.owasp.graphql.nodes.stats import StatsNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project
from apps.slack.models.workspace import Workspace


class StatsQuery:
    """Stats queries."""

    stats_overview = graphene.Field(StatsNode)

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

        slack_workspace_stats = (
            workspace.total_members_count
            if (workspace := Workspace.get_default_workspace())
            else 0
        )

        return StatsNode(
            active_chapters_stats=round_down(active_chapters_stats, 10),
            active_projects_stats=round_down(active_projects_stats, 10),
            contributors_stats=round_down(contributors_stats, 100),
            countries_stats=round_down(countries_stats, 10),
            slack_workspace_stats=round_down(slack_workspace_stats, 100),
        )
