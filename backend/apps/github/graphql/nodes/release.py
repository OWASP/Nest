"""GitHub release GraphQL types."""

from graphene import Field

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.release import Release


class ReleaseNode(BaseNode):
    """GitHub release."""

    author = Field(UserNode)

    class Meta:
        model = Release
        fields = (
            "author",
            "is_pre_release",
            "name",
            "published_at",
            "tag_name",
        )
