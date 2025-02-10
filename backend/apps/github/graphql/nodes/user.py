"""GitHub user GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.user import User


class UserNode(BaseNode):
    """GitHub user node."""

    contributions_count = graphene.Int()
    created_at = graphene.Float()
    updated_at = graphene.Float()
    url = graphene.String()

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "bio",
            "company",
            "email",
            "followers_count",
            "following_count",
            "id",
            "location",
            "login",
            "name",
            "public_repositories_count",
        )

    def resolve_contributions_count(self, info):
        """Resolve user contributions count."""
        if hasattr(self, "contributions_count"):
            return self.contributions_count

        if hasattr(self, "idx_contributions"):
            return sum(rc.get("contributions_count", 0) for rc in self.idx_contributions)

        return 0

    def resolve_created_at(self, info):
        """Resolve user created at."""
        return self.idx_created_at

    def resolve_updated_at(self, info):
        """Resolve user updated at."""
        return self.idx_updated_at

    def resolve_url(self, info):
        """Resolve user URL."""
        return self.url
