"""Defines the GraphQL types for GitHub releases."""

from graphene import Field
from graphene_django import DjangoObjectType

from apps.github.graphql.types.user import UserType
from apps.github.models.release import Release


class ReleaseType(DjangoObjectType):
    """GraphQL type for GitHub releases."""

    author = Field(UserType)

    class Meta:
        """Meta options for the ReleaseType."""

        model = Release
        fields = ("name", "tag_name", "is_pre_release", "published_at", "author")
