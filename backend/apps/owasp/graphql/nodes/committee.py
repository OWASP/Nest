"""OWASP committee GraphQL queries."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.owasp.models.committee import Committee


class CommitteeNode(BaseNode):
    """Committee node."""

    created_at = graphene.Float()
    updated_at = graphene.Float()
    leaders = graphene.List(graphene.String)
    related_urls = graphene.List(graphene.String)
    url = graphene.String()
    top_contributors = graphene.List(UserNode)

    class Meta:
        model = Committee
        fields = (
            "name",
            "summary",
        )

    def resolve_created_at(self, info):
        """Resolve project created at."""
        return self.idx_created_at

    def resolve_related_urls(self, info):
        """Resolve project related URLs."""
        return self.idx_related_urls

    def resolve_top_contributors(self, info):
        """Resolve project top contributors."""
        return [UserNode(**repo) for repo in self.idx_top_contributors]

    def resolve_updated_at(self, info):
        """Resolve project updated at."""
        return self.idx_updated_at

    def resolve_leaders(self, info):
        """Resolve project leaders."""
        return self.idx_leaders

    def resolve_url(self, info):
        """Resolve project URL."""
        return self.idx_url
