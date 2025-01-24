"""Defines the base GraphQL schema types and queries for the application."""

import graphene
from graphene_django import DjangoObjectType


class BaseModelType(DjangoObjectType):
    """Base model type for all Django models."""

    class Meta:
        """Meta options for the BaseModelType."""

        abstract = True


class BaseQuery(graphene.ObjectType):
    """Base query for all graphql queries."""
