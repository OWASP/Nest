"""GraphQL node for User model."""

from graphene_django import DjangoObjectType

from apps.nest.models import User


class AuthUserNode(DjangoObjectType):
    """GraphQL node for User model."""

    class Meta:
        model = User
        fields = ("username",)
