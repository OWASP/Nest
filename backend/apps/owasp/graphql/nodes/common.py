"""OWASP common GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode


class GenericEntityNode(BaseNode):
    """Base node class for OWASP entities with common fields and resolvers."""

    leaders = graphene.List(graphene.String)
    related_urls = graphene.List(graphene.String)
    top_contributors = graphene.List(RepositoryContributorNode)
    updated_at = graphene.Float()
    url = graphene.String()

    class Meta:
        abstract = True

    def resolve_url(self, info) -> str:
        """Resolve URL."""
        return self.idx_url

    def resolve_updated_at(self, info) -> str:
        """Resolve updated at."""
        return self.idx_updated_at

    def resolve_related_urls(self, info) -> list[str]:
        """Resolve related URLs."""
        return self.idx_related_urls

    def resolve_leaders(self, info) -> list[str]:
        """Resolve leaders."""
        return self.idx_leaders

    def resolve_top_contributors(self, info) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return [RepositoryContributorNode(**tc) for tc in self.idx_top_contributors]
