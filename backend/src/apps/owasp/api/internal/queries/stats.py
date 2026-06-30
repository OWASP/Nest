"""OWASP stats GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import round_down
from apps.github.models.user import User
from apps.owasp.api.internal.nodes.stats import StatsNode
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project
from apps.slack.constants import OWASP_WORKSPACE_ID
from apps.slack.models.workspace import Workspace


@strawberry.type
class StatsQuery:
    """Stats queries."""

    @strawberry_django.field
    async def stats_overview(self) -> StatsNode:
        """Resolve stats overview."""
        active_projects_stats = await Project.active_projects.acount()
        active_chapters_stats = await Chapter.active_chapters.acount()
        contributors_stats = await User.objects.acount()
        countries_stats = await (
            Chapter.objects.filter(country__isnull=False)
            .exclude(country="")
            .values("country")
            .distinct()
            .acount()
        )

        workspace = await Workspace.objects.filter(slack_workspace_id=OWASP_WORKSPACE_ID).afirst()
        slack_workspace_stats = workspace.total_members_count if workspace else 0

        return StatsNode(
            active_chapters_stats=round_down(active_chapters_stats, 10),
            active_projects_stats=round_down(active_projects_stats, 10),
            contributors_stats=round_down(contributors_stats, 1000),
            countries_stats=round_down(countries_stats, 10),
            slack_workspace_stats=round_down(slack_workspace_stats, 1000),
        )
