"""GitHub user GraphQL types."""

from apps.common.graphql.nodes import BaseNode
from apps.github.models.user import User


class UserNode(BaseNode):
    """GitHub user."""

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "email",
            "id",
            "login",
            "name",
        )
