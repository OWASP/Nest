"""OWASP common GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode


@strawberry.type
class GenericEntityNode(strawberry.relay.Node):
    """Base node class for OWASP entities with common fields and resolvers."""

    @strawberry_django.field
    def entity_leaders(self) -> list[EntityMemberNode]:
        """Resolve entity leaders."""
        return self.entity_leaders

    @strawberry_django.field
    def leaders(self) -> list[str]:
        """Resolve leaders."""
        return self.idx_leaders

    @strawberry_django.field
    def related_urls(self) -> list[str]:
        """Resolve related URLs."""
        return self.related_urls

    @strawberry_django.field
    def top_contributors(self) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return [RepositoryContributorNode(**tc) for tc in self.idx_top_contributors]

    @strawberry_django.field
    def updated_at(self) -> float:
        """Resolve updated at."""
        return self.idx_updated_at

    @strawberry_django.field
    def url(self) -> str:
        """Resolve URL."""
        return self.idx_url
