"""OWASP project GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.owasp.models.project import Project

RECENT_ISSUES_LIMIT = 10
RECENT_RELEASES_LIMIT = 10


class ProjectNode(BaseNode):
    """Project node."""

    recent_issues = graphene.List(IssueNode)
    recent_releases = graphene.List(ReleaseNode)
    nest_url = graphene.String()

    class Meta:
        model = Project
        fields = (
            "id",
            "key",
            "name",
            "description",
            "summary",
            "tags",
            "custom_tags",
            "level",
            "level_raw",
            "type",
            "type_raw",
            "commits_count",
            "contributors_count",
            "forks_count",
            "open_issues_count",
            "releases_count",
            "stars_count",
            "subscribers_count",
            "watchers_count",
            "languages",
            "licenses",
            "topics",
            "created_at",
            "updated_at",
            "released_at",
            "pushed_at",
            "is_active",
            "track_issues",
            "owners",
            "organizations",
            "repositories",
            "owasp_repository",
        )

    def resolve_nest_url(self, info):
        """Resolve project nest URL."""
        return self.nest_url

    def resolve_recent_issues(self, info):
        """Resolve project recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    def resolve_recent_releases(self, info):
        """Resolve project recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]
