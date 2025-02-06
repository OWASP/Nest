"""GitHub repository GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.models.repository import Repository

RECENT_ISSUES_LIMIT = 10
RECENT_RELEASES_LIMIT = 10


class ContributorType(graphene.ObjectType):
    """contributors type."""

    avatar_url = graphene.String()
    contributions_count = graphene.Int()
    login = graphene.String()
    name = graphene.String()


class RepositoryNode(BaseNode):
    """GitHub repository node."""

    issues = graphene.List(IssueNode)
    languages = graphene.List(graphene.String)
    releases = graphene.List(ReleaseNode)
    topics = graphene.List(graphene.String)
    top_contributors = graphene.List(ContributorType)
    url = graphene.String()

    class Meta:
        model = Repository
        fields = (
            "commits_count",
            "contributors_count",
            "created_at",
            "description",
            "forks_count",
            "key",
            "license",
            "name",
            "open_issues_count",
            "size",
            "stars_count",
            "subscribers_count",
            "updated_at",
        )

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url

    def resolve_top_contributors(self, info):
        """Resolve topContributors."""
        return self.idx_top_contributors

    def resolve_languages(self, info):
        """Resolve languages."""
        return self.languages.keys()

    def resolve_topics(self, info):
        """Resolve topics."""
        return self.topics

    def resolve_issues(self, info):
        """Resolve recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    def resolve_releases(self, info):
        """Resolve recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]
