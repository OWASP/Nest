"""Common GraphQL types."""

from graphene_django import DjangoObjectType


class BaseNode(DjangoObjectType):
    """Base node."""

    class Meta:
        abstract = True
