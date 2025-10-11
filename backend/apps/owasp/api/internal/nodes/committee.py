"""OWASP committee GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.common import GenericEntityNode
from apps.owasp.models.committee import Committee


@strawberry_django.type(Committee, fields=["name", "summary"])
class CommitteeNode(GenericEntityNode):
    """Committee node."""

    @strawberry.field
    def contributors_count(self) -> int:
        """Resolve contributors count."""
        return self.owasp_repository.contributors_count

    @strawberry.field
    def created_at(self) -> float:
        """Resolve created at."""
        return self.idx_created_at

    @strawberry.field
    def forks_count(self) -> int:
        """Resolve forks count."""
        return self.owasp_repository.forks_count

    @strawberry.field
    def issues_count(self) -> int:
        """Resolve issues count."""
        return self.owasp_repository.open_issues_count

    @strawberry.field
    def repositories_count(self) -> int:
        """Resolve repositories count."""
        return 1

    @strawberry.field
    def stars_count(self) -> int:
        """Resolve stars count."""
        return self.owasp_repository.stars_count
