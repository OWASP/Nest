"""GitHub repository GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.repository import Repository


class ContributorType(graphene.ObjectType):
    avatar_url = graphene.String()
    contributions_count = graphene.Int()
    login = graphene.String()
    name = graphene.String()


class RepositoryNode(BaseNode):
    """GitHub repository node."""

    url = graphene.String()
    project = graphene.String()
    top_contributors = graphene.List(ContributorType)

    class Meta:
        model = Repository
        fields = (
            "commits_count",
            "contributors_count",
            "created_at",
            "description",
            "forks_count",
            "languages",
            "name",
            "open_issues_count",
            "stars_count",
            "subscribers_count",
            "topics",
            "updated_at",
        )

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url

    def resolve_top_contributors(self, info):
        """Resolve TopContributors"""
        return self.idx_top_contributors
