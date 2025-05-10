"""OWASP project GraphQL node."""

import graphene

from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.graphql.queries.repository_contributor import RepositoryContributorQuery
from apps.owasp.graphql.nodes.common import GenericEntityNode
from apps.owasp.models.project import Project

RECENT_ISSUES_LIMIT = 5
RECENT_RELEASES_LIMIT = 5


class ProjectNode(GenericEntityNode):
    """Project node."""

    issues_count = graphene.Int()
    key = graphene.String()
    languages = graphene.List(graphene.String)
    level = graphene.String()
    recent_issues = graphene.List(IssueNode)
    recent_releases = graphene.List(ReleaseNode)
    repositories = graphene.List(RepositoryNode)
    repositories_count = graphene.Int()
    topics = graphene.List(graphene.String)
    type = graphene.String()
    top_contributors = graphene.List(
        RepositoryContributorNode,
        limit=graphene.Int(default_value=15),
        organization=graphene.String(required=False),
        excludedUsernames=graphene.List(graphene.String, required=False),
    )

    class Meta:
        model = Project
        fields = (
            "contributors_count",
            "created_at",
            "forks_count",
            "is_active",
            "level",
            "name",
            "open_issues_count",
            "stars_count",
            "summary",
            "type",
        )

    def resolve_issues_count(self, info):
        """Resolve issues count."""
        return self.idx_issues_count

    def resolve_key(self, info):
        """Resolve key."""
        return self.idx_key

    def resolve_languages(self, info):
        """Resolve languages."""
        return self.idx_languages

    def resolve_recent_issues(self, info):
        """Resolve recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    def resolve_recent_releases(self, info):
        """Resolve recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    def resolve_repositories(self, info):
        """Resolve repositories."""
        return self.repositories.order_by("-pushed_at", "-updated_at")

    def resolve_repositories_count(self, info):
        """Resolve repositories count."""
        return self.idx_repositories_count

    def resolve_topics(self, info):
        """Resolve topics."""
        return self.idx_topics

    def resolve_top_contributors(self, info, limit=15, excludedUsernames=None):
        """Resolve top contributors."""
        return RepositoryContributorQuery().resolve_top_contributors(
            info=info,
            limit=limit,
            organization=self.organization.login if hasattr(self, "organization") else None,
            excluded_usernames=excludedUsernames,
            project_key=self.key,
        )
