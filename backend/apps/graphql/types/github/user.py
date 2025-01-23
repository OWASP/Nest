from apps.github.models.user import User
from graphene_django import DjangoObjectType

class UserType(DjangoObjectType):
    class Meta:
        model = User  
        fields = ('id', 'login', 'name', 'email', 'avatar_url')