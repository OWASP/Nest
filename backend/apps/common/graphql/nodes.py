"""Common GraphQL nodes."""

#!/usr/bin/env python3
from graphene_django import DjangoObjectType


class BaseNode(DjangoObjectType):
    """Base node."""

    class Meta:
        abstract = True
