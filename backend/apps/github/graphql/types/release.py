from graphene import Field
from graphene_django import DjangoObjectType

from apps.github.graphql.types.user import UserType
from apps.github.models.release import Release


class ReleaseType(DjangoObjectType):
    author = Field(UserType)

    class Meta:
        model = Release
        fields = ("name", "tag_name", "is_pre_release", "published_at", "author")
