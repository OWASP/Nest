"""
This module defines the base GraphQL schema types and queries for the application.
"""
import graphene
from graphene_django import DjangoObjectType


class BaseModelType(DjangoObjectType):
    class Meta:
        abstract = True


class BaseQuery(graphene.ObjectType):
    """Base query for all graphql queries"""
