"""OWASP committee GraphQL node."""

import strawberry_django

from apps.owasp.api.internal.nodes.common import GenericEntityNode
from apps.owasp.models.committee import Committee


@strawberry_django.type(Committee, fields=["name", "summary"])
class CommitteeNode(GenericEntityNode):
    """Committee node."""

    @strawberry_django.field
    def contributors_count(self, root: Committee) -> int:
        """Resolve contributors count."""
        return root.owasp_repository.contributors_count if root.owasp_repository else 0

    @strawberry_django.field
    def created_at(self, root: Committee) -> float | None:
        """Resolve created at."""
        return root.idx_created_at

    @strawberry_django.field
    def forks_count(self, root: Committee) -> int:
        """Resolve forks count."""
        return root.owasp_repository.forks_count if root.owasp_repository else 0

    @strawberry_django.field
    def issues_count(self, root: Committee) -> int:
        """Resolve issues count."""
        return root.owasp_repository.open_issues_count if root.owasp_repository else 0

    @strawberry_django.field
    def repositories_count(self, root: Committee) -> int:
        """Resolve repositories count."""
        return 1

    @strawberry_django.field
    def stars_count(self, root: Committee) -> int:
        """Resolve stars count."""
        return root.owasp_repository.stars_count if root.owasp_repository else 0
