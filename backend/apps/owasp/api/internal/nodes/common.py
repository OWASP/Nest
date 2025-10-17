"""OWASP common GraphQL node."""

import strawberry

from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode


@strawberry.type
class GenericEntityNode(strawberry.relay.Node):
    """Base node class for OWASP entities with common fields and resolvers."""

    @strawberry.field
    def entity_leaders(self) -> list[EntityMemberNode]:
        """Resolve entity leaders."""
        return self.entity_leaders

    @strawberry.field
    def leaders(self) -> list[str]:
        """Resolve leaders."""
        return self.idx_leaders

    @strawberry.field
    def related_urls(self) -> list[str]:
        """Resolve related URLs."""
        return self.idx_related_urls

    @strawberry.field
    def top_contributors(self) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return [RepositoryContributorNode(**tc) for tc in self.idx_top_contributors]

    @strawberry.field
    def updated_at(self) -> float:
        """Resolve updated at."""
        return self.idx_updated_at

    @strawberry.field
    def url(self) -> str:
        """Resolve URL."""
        return self.idx_url
