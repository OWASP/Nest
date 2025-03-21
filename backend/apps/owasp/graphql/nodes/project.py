"""OWASP project GraphQL node."""

import graphene

from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
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
    recent_issues = graphene.List(
        IssueNode,
        distinct=graphene.Boolean(default_value=False),  # Add distinct argument
    )
    recent_releases = graphene.List(
        ReleaseNode,
        distinct=graphene.Boolean(default_value=False),  # Add distinct argument
    )
    repositories = graphene.List(RepositoryNode)
    repositories_count = graphene.Int()
    topics = graphene.List(graphene.String)
    type = graphene.String()

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

    def resolve_recent_issues(root, info, limit=RECENT_ISSUES_LIMIT, distinct=False):  
        """Resolve recent issues with optional distinct filtering."""
        query = Issue.objects.order_by("author_id", "repository_id", "-created_at")  

        if distinct:
            query = query.distinct("author_id", "repository_id")  

        return query[:limit]

    def resolve_recent_releases(self, info, distinct=False):
        """Resolve recent releases with optional distinct filtering."""
        query = self.published_releases.order_by("author_id", "repository_id", "-published_at")

        if distinct:
            query = query.distinct("author_id", "repository_id")  

        return query[:RECENT_RELEASES_LIMIT]



    def resolve_repositories(self, info):
        """Resolve repositories."""
        return self.repositories.order_by("-pushed_at", "-updated_at")

    def resolve_repositories_count(self, info):
        """Resolve repositories count."""
        return self.idx_repositories_count

    def resolve_topics(self, info):
        """Resolve topics."""
        return self.idx_topics
