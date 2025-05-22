"""OWASP chapter GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.graphql.nodes.common import GenericEntityNode
from apps.owasp.models.chapter import Chapter


@strawberry.type
class GeoLocationType:
    """Geographic location type."""

    lat: float
    lng: float


@strawberry_django.type(
    Chapter,
    fields=[
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

    @strawberry.field
    def created_at(self) -> float:
        """Resolve created at."""
        return self.idx_created_at

    @strawberry.field
    def geo_location(self) -> GeoLocationType | None:
        """Resolve geographic location."""
        if self.latitude is not None and self.longitude is not None:
            return GeoLocationType(lat=self.latitude, lng=self.longitude)
        return None

    @strawberry.field
    def key(self) -> str:
        """Resolve key."""
        return self.idx_key

    @strawberry.field
    def suggested_location(self) -> str | None:
        """Resolve suggested location."""
        return self.idx_suggested_location
