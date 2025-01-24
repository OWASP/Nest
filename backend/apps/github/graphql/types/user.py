from graphene_django import DjangoObjectType

from apps.github.models.user import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "login", "name", "email", "avatar_url")
