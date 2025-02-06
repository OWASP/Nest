"""OWASP project GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.owasp.models.project import Project

RECENT_ISSUES_LIMIT = 10
RECENT_RELEASES_LIMIT = 10


class ProjectNode(BaseNode):
    """Project node."""

    recent_issues = graphene.List(IssueNode)
    recent_releases = graphene.List(ReleaseNode)
    repositories = graphene.List(RepositoryNode)

    class Meta:
        model = Project
        fields = ()

    def resolve_recent_issues(self, info):
        """Resolve project recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    def resolve_recent_releases(self, info):
        """Resolve project recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    def resolve_repositories(self, info, repo_key=None):
        """Resolve repositories, optionally filtered by repo_key."""
        if hasattr(self, "repo_key") and self.repo_key:
            return self.repositories.filter(key=self.repo_key)
        return self.repositories.all()
