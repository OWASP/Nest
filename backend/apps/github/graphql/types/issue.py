"""Defines the GraphQL types for GitHub issues."""

from graphene_django import DjangoObjectType

from apps.github.models.issue import Issue


class IssueType(DjangoObjectType):
    """GraphQL type for GitHub issues."""

    class Meta:
        """Meta options for the IssueType."""

        model = Issue
        fields = ("number", "title", "created_at", "comments_count", "author", "state")
