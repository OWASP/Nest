"""GitHub release GraphQL node."""

import strawberry
import strawberry_django
from strawberry.types import Info

from apps.github.api.internal.dataloaders.release import RELEASE_URL_BY_ID_LOADER
from apps.github.api.internal.dataloaders.repository import (
    REPOSITORY_BY_RELEASE_ID_LOADER,
    REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER,
)
from apps.github.api.internal.nodes.user import UserNode
from apps.github.models.release import Release


@strawberry_django.type(
    Release,
    fields=[
        "is_pre_release",
        "name",
        "published_at",
        "tag_name",
    ],
)
class ReleaseNode(strawberry.relay.Node):
    """GitHub release node."""

    author: UserNode | None = strawberry_django.field()

    @strawberry_django.field
    async def organization_name(self, root: Release, info: Info) -> str | None:
        """Resolve organization name."""
        repository = await info.context.github_dataloaders[REPOSITORY_BY_RELEASE_ID_LOADER].load(
            root.pk
        )
        return repository.organization.login if repository and repository.organization else None

    @strawberry_django.field
    async def project_name(self, root: Release, info: Info) -> str | None:
        """Resolve project name."""
        return await info.context.github_dataloaders[
            REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER
        ].load(root.pk)

    @strawberry_django.field
    async def repository_name(self, root: Release, info: Info) -> str | None:
        """Resolve repository name."""
        repository = await info.context.github_dataloaders[REPOSITORY_BY_RELEASE_ID_LOADER].load(
            root.pk
        )
        return repository.name if repository else None

    @strawberry_django.field
    async def url(self, root: Release, info: Info) -> str:
        """Resolve URL."""
        return await info.context.github_dataloaders[RELEASE_URL_BY_ID_LOADER].load(root.pk)
