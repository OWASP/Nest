"""Defines the GraphQL types for GitHub users."""

from graphene_django import DjangoObjectType

from apps.github.models.user import User


class UserType(DjangoObjectType):
    """GraphQL type for GitHub users."""

    class Meta:
        """Meta options for the UserType."""

        model = User
        fields = ("id", "login", "name", "email", "avatar_url")
