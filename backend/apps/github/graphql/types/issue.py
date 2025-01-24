from graphene_django import DjangoObjectType

from apps.github.models.issue import Issue


class IssueType(DjangoObjectType):
    class Meta:
        model = Issue
        fields = ("number", "title", "created_at", "comments_count", "author", "state")
