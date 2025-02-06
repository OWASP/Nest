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

    country = graphene.String()
    created_at = graphene.Float()
    geo_location = graphene.Field(GeoLocationType)
    is_active = graphene.Boolean()
    tags = graphene.String()
    key = graphene.String()
    leaders = graphene.List(graphene.String)
    meetup_group = graphene.String()
    postal_code = graphene.String()
    region = graphene.String()
    related_urls = graphene.List(graphene.String)
    suggested_location = graphene.String()
    top_contributors = graphene.List(UserNode)
    updated_at = graphene.Float()
    url = graphene.String()

    class Meta:
        model = Chapter
        only_fields = (
            "country",
            "name",
            "summary",
        )

    def resolve_country(self, info):
        """Resolve chapter country."""
        return self.idx_country

    def resolve_created_at(self, info):
        """Resolve chapter created at."""
        return self.idx_created_at

    def resolve_geo_location(self, info):
        """Resolve chapter geographic location."""
        return GeoLocationType(lat=self.latitude, lng=self.longitude)

    def resolve_tags(self, info):
        """Resolve chapter tags."""
        return self.idx_tags

    def resolve_is_active(self, info):
        """Resolve chapter is active."""
        return self.idx_is_active

    def resolve_key(self, info):
        """Resolve chapter key."""
        return self.idx_key

    def resolve_leaders(self, info):
        """Resolve chapter leaders."""
        return self.idx_leaders

    def resolve_meetup_group(self, info):
        """Resolve chapter meetup group."""
        return self.idx_meetup_group

    def resolve_postal_code(self, info):
        """Resolve chapter postal code."""
        return self.idx_postal_code

    def resolve_region(self, info):
        """Resolve chapter region."""
        return self.idx_region

    def resolve_related_urls(self, info):
        """Resolve chapter related URLs."""
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
