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
    def contribution_stats(self) -> strawberry.scalars.JSON | None:
        """Resolve contribution stats with camelCase keys."""
        return deep_camelize(self.contribution_stats)

    @strawberry_django.field
    def created_at(self) -> float:
        """Resolve created at."""
        return self.idx_created_at

    @strawberry_django.field
    def geo_location(self) -> GeoLocationType | None:
        """Resolve geographic location."""
        return (
            GeoLocationType(lat=self.latitude, lng=self.longitude)
            if self.latitude is not None and self.longitude is not None
            else None
        )

    @strawberry_django.field
    def key(self) -> str:
        """Resolve key."""
        return self.idx_key

    @strawberry_django.field
    def suggested_location(self) -> str | None:
        """Resolve suggested location."""
        return self.idx_suggested_location
