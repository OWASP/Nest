"""OWASP project GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.nodes.user import UserNode
from apps.owasp.models.project import Project

RECENT_ISSUES_LIMIT = 10
RECENT_RELEASES_LIMIT = 10


class ProjectNode(BaseNode):
    """Project node."""

    issues_count = graphene.Int()
    key = graphene.String()
    leaders = graphene.List(graphene.String)
    languages = graphene.List(graphene.String)
    repositories_count = graphene.Int()
    topics = graphene.List(graphene.String)
    updated_at = graphene.Float()
    url = graphene.String()

    recent_issues = graphene.List(IssueNode)
    recent_releases = graphene.List(ReleaseNode)
    repositories = graphene.List(RepositoryNode)
    top_contributors = graphene.List(UserNode)

    class Meta:
        model = Project
        fields = (
            "contributors_count",
            "forks_count",
            "is_active",
            "level",
            "name",
            "stars_count",
            "summary",
            "type",
        )

    def resolve_issues_count(self, info):
        """Resolve project issues count."""
        return self.idx_issues_count

    def resolve_key(self, info):
        """Resolve project key."""
        return self.idx_key

    def resolve_languages(self, info):
        """Resolve project languages."""
        return self.idx_languages

    def resolve_leaders(self, info):
        """Resolve project leaders."""
        return self.idx_leaders

    def resolve_recent_issues(self, info):
        """Resolve project recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    def resolve_recent_releases(self, info):
        """Resolve project recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    def resolve_repositories(self, info):
        """Resolve project repositories."""
        return self.repositories.order_by("-pushed_at", "-updated_at")

    def resolve_repositories_count(self, info):
        """Resolve project repositories count."""
        return self.idx_repositories_count

    def resolve_repositories_indexed(self, info):
        """Resolve project indexed repositories."""
        return [RepositoryNode(**repo) for repo in self.idx_repositories]

    def resolve_topics(self, info):
        """Resolve project topics."""
        return self.idx_topics

    def resolve_top_contributors(self, info):
        """Resolve project top contributors."""
        return [UserNode(**repo) for repo in self.idx_top_contributors]

    def resolve_updated_at(self, info):
        """Resolve project updated at."""
        return self.idx_updated_at

    def resolve_url(self, info):
        """Resolve project URL."""
        return self.idx_url
