"""OWASP snapshot GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.api.internal.dataloaders.snapshot import (
    NEW_CHAPTERS_BY_SNAPSHOT_ID,
    NEW_ISSUES_BY_SNAPSHOT_ID,
    NEW_PROJECTS_BY_SNAPSHOT_ID,
    NEW_RELEASES_BY_SNAPSHOT_ID,
    NEW_USERS_BY_SNAPSHOT_ID,
)
from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.snapshot import Snapshot


@strawberry_django.type(
    Snapshot,
    fields=[
        "created_at",
        "end_at",
        "start_at",
        "title",
    ],
)
class SnapshotNode(strawberry.relay.Node):
    """Snapshot node."""

    @strawberry_django.field
    async def new_chapters(self, root: Snapshot, info: strawberry.Info) -> list[ChapterNode]:
        """Resolve new chapters."""
        return await info.context.owasp_dataloaders[NEW_CHAPTERS_BY_SNAPSHOT_ID].load(root.pk)

    @strawberry_django.field
    async def new_issues(self, root: Snapshot, info: strawberry.Info) -> list[IssueNode]:
        """Resolve new issues."""
        return await info.context.owasp_dataloaders[NEW_ISSUES_BY_SNAPSHOT_ID].load(root.pk)

    @strawberry_django.field
    async def new_projects(self, root: Snapshot, info: strawberry.Info) -> list[ProjectNode]:
        """Resolve new projects."""
        return await info.context.owasp_dataloaders[NEW_PROJECTS_BY_SNAPSHOT_ID].load(root.pk)

    @strawberry_django.field
    async def new_releases(self, root: Snapshot, info: strawberry.Info) -> list[ReleaseNode]:
        """Resolve new releases."""
        return await info.context.owasp_dataloaders[NEW_RELEASES_BY_SNAPSHOT_ID].load(root.pk)

    @strawberry_django.field
    async def new_users(self, root: Snapshot, info: strawberry.Info) -> list[UserNode]:
        """Resolve new users."""
        return await info.context.owasp_dataloaders[NEW_USERS_BY_SNAPSHOT_ID].load(root.pk)

    @strawberry_django.field(only=["key"])
    def key(self, root: Snapshot) -> str:
        """Resolve key."""
        return root.key
