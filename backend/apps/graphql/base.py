import graphene
from graphene_django import DjangoObjectType

class BaseModelType(DjangoObjectType):
    class Meta:
        abstract = True

class BaseQuery(graphene.ObjectType):
    pass