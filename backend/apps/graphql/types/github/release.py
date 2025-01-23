from apps.github.models.release import Release
from apps.github.models.user import User
from graphene_django import DjangoObjectType
from apps.graphql.types.github.user import UserType
from graphene import Field


class ReleaseType(DjangoObjectType):
    author = Field(UserType)
    class Meta:
        model = Release
        fields = ('name', 'tag_name', 'is_pre_release', 'published_at', 'author')