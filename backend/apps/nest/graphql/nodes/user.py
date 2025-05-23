from graphene_django import DjangoObjectType
from apps.nest.models import User

class AuthUserNode(DjangoObjectType):
    class Meta:
        model = User
        fields = ("username",)