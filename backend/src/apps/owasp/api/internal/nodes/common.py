"""OWASP common GraphQL node."""

import strawberry
import strawberry_django


@strawberry.type
class GenericEntityNode(strawberry.relay.Node):
    """Base node class for OWASP entities with common fields and resolvers."""

    @strawberry_django.field(only=["leaders_raw"])
    def leaders(self, root) -> list[str]:
        """Resolve leaders."""
        return root.idx_leaders

    @strawberry_django.field(only=["related_urls"])
    def related_urls(self, root) -> list[str]:
        """Resolve related URLs."""
        return root.related_urls

    @strawberry_django.field(
        only=["updated_at", "owasp_repository__updated_at"], select_related=["owasp_repository"]
    )
    def updated_at(self, root) -> str:
        """Resolve updated at."""
        return root.idx_updated_at

    @strawberry_django.field(only=["key"])
    def url(self, root) -> str:
        """Resolve URL."""
        return root.idx_url
