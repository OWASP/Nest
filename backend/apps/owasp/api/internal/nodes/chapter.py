"""OWASP chapter GraphQL node."""

import strawberry
import strawberry_django

from apps.core.utils.index import deep_camelize
from apps.owasp.api.internal.nodes.common import GenericEntityNode
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

    @strawberry_django.field
    def contribution_stats(self, root: Chapter) -> strawberry.scalars.JSON | None:
        """Resolve contribution stats with camelCase keys."""
        return deep_camelize(root.contribution_stats)

    @strawberry_django.field
    def created_at(self, root: Chapter) -> float:
        """Resolve created at."""
        return root.idx_created_at

    @strawberry_django.field
    def geo_location(self, root: Chapter) -> GeoLocationType | None:
        """Resolve geographic location."""
        return (
            GeoLocationType(lat=root.latitude, lng=root.longitude)
            if root.latitude is not None and root.longitude is not None
            else None
        )

    @strawberry_django.field
    def key(self, root: Chapter) -> str:
        """Resolve key."""
        return root.idx_key

    @strawberry_django.field
    def suggested_location(self, root: Chapter) -> str | None:
        """Resolve suggested location."""
        return root.idx_suggested_location
