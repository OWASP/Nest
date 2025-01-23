from apps.github.models.issue import Issue
from apps.github.models.user import User
from graphene_django import DjangoObjectType

class IssueType(DjangoObjectType):
    class Meta:
        model = Issue
        fields = ('number', 'title', 'created_at', 'comments_count', 'author', 'state')