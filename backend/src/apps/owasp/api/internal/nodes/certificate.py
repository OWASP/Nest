"""OWASP Certificate GraphQL node."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.models.crp.certificate import Certificate

if TYPE_CHECKING:
    from apps.owasp.api.internal.nodes.chapter import ChapterNode
    from apps.owasp.api.internal.nodes.project import ProjectNode


@strawberry_django.type(
    Certificate,
    fields=[
        "id",
        "issued_at",
        "message",
        "score",
        "title",
    ],
)
class CertificateNode:
    """Certificate node."""

    @strawberry_django.field(select_related=["recipient"])
    def recipient(self, root: Certificate) -> UserNode:
        """Resolve the recipient user."""
        return root.recipient

    @strawberry_django.field(select_related=["recipient"])
    def github_user(self, root: Certificate) -> UserNode:
        """Resolve the associated GitHub user (alias for recipient)."""
        return root.recipient

    @strawberry_django.field(select_related=["issuer"])
    def issuer(self, root: Certificate) -> UserNode | None:
        """Resolve the issuer user."""
        return root.issuer

    @strawberry_django.field(select_related=["project"])
    def project(
        self, root: Certificate
    ) -> Annotated["ProjectNode", strawberry.lazy("apps.owasp.api.internal.nodes.project")] | None:
        """Resolve associated project."""
        return root.project

    @strawberry_django.field(select_related=["chapter"])
    def chapter(
        self, root: Certificate
    ) -> Annotated["ChapterNode", strawberry.lazy("apps.owasp.api.internal.nodes.chapter")] | None:
        """Resolve associated chapter."""
        return root.chapter

    @strawberry_django.field
    def is_verified(self, root: Certificate) -> bool:
        """Resolve whether the certificate is active/verified."""
        return root.is_verified

    @strawberry_django.field
    def tier(self, root: Certificate) -> str:
        """Resolve the human-readable tier level (e.g. 'Level 1')."""
        return root.get_tier_display() if root.tier else ""
