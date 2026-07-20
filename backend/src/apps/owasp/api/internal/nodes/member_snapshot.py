"""OWASP member snapshot GraphQL node."""

import strawberry
import strawberry_django
from strawberry.types import Info

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.api.internal.dataloaders.member_snapshot import (
    COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER,
    ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER,
    MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER,
    PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER,
    TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER,
)
from apps.owasp.models.member_snapshot import MemberSnapshot


@strawberry_django.type(
    MemberSnapshot,
    fields=[
        "start_at",
        "end_at",
        "contribution_heatmap_data",
        "communication_heatmap_data",
        "chapter_contributions",
        "project_contributions",
        "repository_contributions",
        "channel_communications",
    ],
)
class MemberSnapshotNode(strawberry.relay.Node):
    """Member snapshot node."""

    @strawberry_django.field
    async def commits_count(self, root: MemberSnapshot, info: Info) -> int:
        """Resolve commits count."""
        return await info.context.owasp_dataloaders[COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field(select_related=["github_user"])
    def github_user(self, root: MemberSnapshot) -> UserNode:
        """Resolve GitHub user."""
        return root.github_user

    @strawberry_django.field
    async def issues_count(self, root: MemberSnapshot, info: Info) -> int:
        """Resolve issues count."""
        return await info.context.owasp_dataloaders[ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field
    async def pull_requests_count(self, root: MemberSnapshot, info: Info) -> int:
        """Resolve pull requests count."""
        return await info.context.owasp_dataloaders[
            PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER
        ].load(root.pk)

    @strawberry_django.field
    async def messages_count(self, root: MemberSnapshot, info: Info) -> int:
        """Resolve Slack messages count."""
        return await info.context.owasp_dataloaders[MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field
    async def total_contributions(self, root: MemberSnapshot, info: Info) -> int:
        """Resolve total contributions."""
        return await info.context.owasp_dataloaders[
            TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER
        ].load(root.pk)
