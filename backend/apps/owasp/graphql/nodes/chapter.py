"""OWASP chapter GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.owasp.models.chapter import Chapter


class GeoLocationType(graphene.ObjectType):
    """Geographic location type."""

    lat = graphene.Float()
    lng = graphene.Float()


class ChapterNode(BaseNode):
    """Chapter node."""

    key = graphene.String()
    related_urls = graphene.List(graphene.String)
    suggested_location = graphene.String()
    updated_at = graphene.Float()
    url = graphene.String()

    geo_location = graphene.Field(GeoLocationType)
    top_contributors = graphene.List(UserNode)

    class Meta:
        model = Chapter
        only_fields = (
            "country",
            "is_active",
            "meetup_group",
            "name",
            "postal_code",
            "region",
            "summary",
            "tags",
        )

    def resolve_geo_location(self, info):
        """Resolve chapter geographic location."""
        return GeoLocationType(lat=self.latitude, lng=self.longitude)

    def resolve_key(self, info):
        """Resolve chapter key."""
        return self.idx_key

    def resolve_related_urls(self, info):
        """Resolve chapter related urls."""
        return self.idx_related_urls

    def resolve_suggested_location(self, info):
        """Resolve chapter suggested location."""
        return self.idx_suggested_location

    def resolve_top_contributors(self, info):
        """Resolve chapter top contributors."""
        return [UserNode(**repo) for repo in self.idx_top_contributors]

    def resolve_updated_at(self, info):
        """Resolve updated at."""
        return self.idx_updated_at

    def resolve_url(self, info):
        """Resolve url."""
        return self.idx_url
