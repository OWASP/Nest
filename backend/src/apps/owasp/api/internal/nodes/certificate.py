"""OWASP Certificate GraphQL node."""

import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.models.crp.certificate import Certificate


@strawberry_django.type(
    Certificate,
    fields=[
        "id",
        "issued_at",
        "score",
    ],
)
class CertificateNode:
    """Certificate node."""

    @strawberry_django.field
    def tier(self, root: Certificate) -> str:
        """Resolve the human-readable tier level (e.g. 'Level 1')."""
        return root.get_tier_display()

    @strawberry_django.field
    def is_verified(self, root: Certificate) -> bool:
        """Resolve whether the certificate is active/verified."""
        return not root.is_revoked

    @strawberry_django.field(select_related=["github_user"])
    def github_user(self, root: Certificate) -> UserNode:
        """Resolve the associated GitHub user."""
        return root.github_user
