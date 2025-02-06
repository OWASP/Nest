"""GitHub user GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.user import User


class UserNode(BaseNode):
    """GitHub user node."""

    contributions_count = graphene.Int()

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "email",
            "id",
            "login",
            "name",
        )

    def resolve_contributions_count(self, info):
        """Resolve user contributions count."""
        return self.contributions_count
