"""OWASP chapter GraphQL node."""

import strawberry
import strawberry_django

from apps.core.utils.index import deep_camelize
from apps.owasp.api.internal.dataloaders.chapter import (
    ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER,
    ENTITY_LEADERS_BY_CHAPTER_ID_LOADER,
)
from apps.owasp.api.internal.nodes.common import GenericEntityNode
from apps.owasp.api.internal.nodes.entity_channel import EntityChannelNode
from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode
from apps.owasp.models.chapter import Chapter


@strawberry.type
class GeoLocationType:
    """Geographic location type."""

    lat: float
    lng: float


@strawberry_django.type(
    Chapter,
    fields=[
        "contribution_data",
        "country",
        "is_active",
        "meetup_group",
        "name",
        "postal_code",
        "region",
        "summary",
        "tags",
    ],
)
class ChapterNode(GenericEntityNode):
    """Chapter node."""

    @strawberry_django.field(only=["contribution_stats"])
    def contribution_stats(self, root: Chapter) -> strawberry.scalars.JSON | None:
        """Resolve contribution stats with camelCase keys."""
        return deep_camelize(root.contribution_stats)

    @strawberry_django.field(
        only=["created_at", "owasp_repository__created_at"], select_related=["owasp_repository"]
    )
    def created_at(self, root: Chapter) -> str:
        """Resolve created at."""
        return root.idx_created_at

    @strawberry_django.field(only=["latitude", "longitude"])
    def geo_location(self, root: Chapter) -> GeoLocationType | None:
        """Resolve geographic location."""
        return (
            GeoLocationType(lat=root.latitude, lng=root.longitude)
            if root.latitude is not None and root.longitude is not None
            else None
        )

    @strawberry_django.field
    async def entity_channels(
        self, root: Chapter, info: strawberry.Info
    ) -> list[EntityChannelNode]:
        """Resolve entity channels."""
        return await info.context.owasp_dataloaders[ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field
    async def entity_leaders(self, root: Chapter, info: strawberry.Info) -> list[EntityMemberNode]:
        """Resolve entity leaders."""
        return await info.context.owasp_dataloaders[ENTITY_LEADERS_BY_CHAPTER_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field(only=["key"])
    def key(self, root: Chapter) -> str:
        """Resolve key."""
        return root.idx_key

    @strawberry_django.field(only=["suggested_location"])
    def suggested_location(self, root: Chapter) -> str | None:
        """Resolve suggested location."""
        return root.idx_suggested_location
