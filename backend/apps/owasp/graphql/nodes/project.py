"""GraphQL types for OWASP projects."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.owasp.models.project import Project


class ProjectNode(BaseNode):
    """Project node."""

    recent_issues = graphene.List(
        IssueNode,
        limit=graphene.Int(default_value=10),
        state=graphene.String(default_value="open"),
    )
    recent_releases = graphene.List(ReleaseNode, limit=graphene.Int(default_value=10))

    class Meta:
        model = Project
        fields = ()

    def resolve_recent_issues(self, info, limit=10, state="open"):
        """Resolve recent issues for the project."""
        return Issue.objects.filter(repository__in=self.repositories.all(), state=state).order_by(
            "-created_at"
        )[:limit]

    def resolve_recent_releases(self, info, limit=10):
        """Resolve recent releases for the project."""
        return Release.objects.filter(
            repository__in=self.repositories.all(), is_draft=False, published_at__isnull=False
        ).order_by("-published_at")[:limit]
