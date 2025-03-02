"""OWASP snapshot GraphQL node."""

import graphene

from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.user import UserNode
from apps.owasp.graphql.nodes.chapter import ChapterNode
from apps.owasp.graphql.nodes.common import GenericEntityNode
from apps.owasp.graphql.nodes.project import ProjectNode
from apps.owasp.models.snapshot import Snapshot

RECENT_ISSUES_LIMIT = 10
RECENT_RELEASES_LIMIT = 10
RECENT_PROJECTS_LIMIT = 10
RECENT_USERS_LIMIT = 10


class SnapshotNode(GenericEntityNode):
    """Snapshot node."""

    key = graphene.String()
    status = graphene.String()
    error_message = graphene.String()
    new_chapters = graphene.List(ChapterNode)
    new_issues = graphene.List(IssueNode)
    new_projects = graphene.List(ProjectNode)
    new_releases = graphene.List(ReleaseNode)
    new_users = graphene.List(UserNode)

    class Meta:
        model = Snapshot
        fields = (
            "title",
            "created_at",
            "updated_at",
            "start_at",
            "end_at",
        )

    def resolve_key(self, info):
        """Resolve key."""
        return self.key

    def resolve_status(self, info):
        """Resolve status."""
        return self.status

    def resolve_error_message(self, info):
        """Resolve error message."""
        return self.error_message

    def resolve_new_chapters(self, info):
        """Resolve new chapters."""
        return self.new_chapters.all()

    def resolve_new_issues(self, info):
        """Resolve recent new issues."""
        return self.new_issues.order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    def resolve_new_projects(self, info):
        """Resolve recent new projects."""
        return self.new_projects.order_by("-created_at")[:RECENT_PROJECTS_LIMIT]

    def resolve_new_releases(self, info):
        """Resolve recent new releases."""
        return self.new_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    def resolve_new_users(self, info):
        """Resolve recent new users."""
        return self.new_users.order_by("-created_at")[:RECENT_USERS_LIMIT]
