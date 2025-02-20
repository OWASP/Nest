"""OWASP chapter GraphQL node."""

import graphene

from apps.owasp.graphql.nodes.common import GenericEntityNode
from apps.owasp.models.chapter import Chapter


class GeoLocationType(graphene.ObjectType):
    """Geographic location type."""

    lat = graphene.Float()
    lng = graphene.Float()


class ChapterNode(GenericEntityNode):
    """Chapter node."""

    key = graphene.String()
    suggested_location = graphene.String()
    geo_location = graphene.Field(GeoLocationType)

    class Meta:
        model = Chapter
        fields = (
            "created_at",
            "is_active",
            "country",
            "meetup_group",
            "name",
            "postal_code",
            "region",
            "summary",
            "tags",
        )

    def resolve_geo_location(self, info):
        """Resolve geographic location."""
        return GeoLocationType(lat=self.latitude, lng=self.longitude)

    def resolve_key(self, info):
        """Resolve key."""
        return self.idx_key

    def resolve_suggested_location(self, info):
        """Resolve suggested location."""
        return self.idx_suggested_location
