"""OWASP certificate GraphQL queries."""

import re

import strawberry
import strawberry_django

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.certificate import CertificateNode
from apps.owasp.models.crp.certificate import (
    CERTIFICATE_ID_ALPHABET,
    CERTIFICATE_ID_LENGTH,
    Certificate,
)

CERTIFICATE_ID_RE = re.compile(
    rf"^[{re.escape(CERTIFICATE_ID_ALPHABET)}]{{{CERTIFICATE_ID_LENGTH}}}$"
)


@strawberry.type
class CertificateQuery:
    """Certificate queries."""

    @strawberry_django.field
    def certificate(self, certificate_id: str) -> CertificateNode | None:
        """Resolve certificate by ID."""
        if not CERTIFICATE_ID_RE.fullmatch(certificate_id):
            return None

        try:
            return Certificate.objects.select_related(
                "recipient",
                "issuer",
                "project",
                "chapter",
            ).get(id=certificate_id)
        except Certificate.DoesNotExist:
            return None

    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def my_certificates(self, info: strawberry.types.Info) -> list[CertificateNode]:
        """Resolve current authenticated user's certificates."""
        user = info.context.request.user
        if getattr(user, "github_user", None) is None:
            return []

        return (
            Certificate.objects.select_related(
                "recipient",
                "issuer",
                "project",
                "chapter",
            )
            .filter(recipient=user.github_user, is_revoked=False)
            .order_by("-issued_at")
        )
