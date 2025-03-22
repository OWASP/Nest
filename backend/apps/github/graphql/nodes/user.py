"""GitHub user GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.user import User


class RepositoryType(graphene.ObjectType):
    """Repository type for nested objects."""

    key = graphene.String()
    owner_key = graphene.String()


class IssueType(graphene.ObjectType):
    """GitHub issue type."""

    created_at = graphene.Float()
    comments_count = graphene.Int()
    number = graphene.Int()
    repository = graphene.Field(RepositoryType)
    title = graphene.String()
    url = graphene.String()


class ReleaseType(graphene.ObjectType):
    """GitHub release type."""

    is_pre_release = graphene.Boolean()
    name = graphene.String()
    published_at = graphene.Float()
    repository = graphene.Field(RepositoryType)
    tag_name = graphene.String()
    url = graphene.String()


class UserNode(BaseNode):
    """GitHub user node."""

    created_at = graphene.Float()
    issues = graphene.List(IssueType)
    issues_count = graphene.Int()
    releases = graphene.List(ReleaseType)
    releases_count = graphene.Int()
    updated_at = graphene.Float()
    url = graphene.String()

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "bio",
            "company",
            "email",
            "followers_count",
            "following_count",
            "id",
            "location",
            "login",
            "name",
            "public_repositories_count",
        )

    def resolve_created_at(self, info):
        """Resolve created at."""
        return self.idx_created_at

    def resolve_updated_at(self, info):
        """Resolve updated at."""
        return self.idx_updated_at

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url

    def resolve_issues(self, info):
        """Resolve issues."""
        return self.idx_issues

    def resolve_issues_count(self, info):
        """Resolve issues count."""
        return self.idx_issues_count

    def resolve_releases(self, info):
        """Resolve releases."""
        return self.idx_releases

    def resolve_releases_count(self, info):
        """Resolve releases count."""
        return self.idx_releases_count
