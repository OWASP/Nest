"""OWASP app entity channel GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.dataloaders.entity_channel import (
    EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER,
    NAME_BY_ENTITY_CHANNEL_ID_LOADER,
)
from apps.owasp.models.entity_channel import EntityChannel


@strawberry_django.type(
    EntityChannel,
    fields=[
        "is_active",
        "is_default",
        "is_reviewed",
        "platform",
    ],
)
class EntityChannelNode(strawberry.relay.Node):
    """Entity channel node."""

    @strawberry_django.field
    async def external_id(self, root: EntityChannel, info: strawberry.Info) -> str | None:
        """Resolve platform-specific channel ID."""
        return await info.context.owasp_dataloaders[EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field
    async def name(self, root: EntityChannel, info: strawberry.Info) -> str | None:
        """Resolve channel display name."""
        return await info.context.owasp_dataloaders[NAME_BY_ENTITY_CHANNEL_ID_LOADER].load(root.pk)
