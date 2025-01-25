"""GitHub user GraphQL node."""

from apps.common.graphql.nodes import BaseNode
from apps.github.models.user import User


class UserNode(BaseNode):
    """GitHub user node."""

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "email",
            "id",
            "login",
            "name",
        )
