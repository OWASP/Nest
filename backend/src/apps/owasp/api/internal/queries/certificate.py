"""OWASP certificate GraphQL queries."""

import strawberry
import strawberry_django
from django.core.exceptions import ValidationError

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.certificate import CertificateNode
from apps.owasp.models.crp.certificate import Certificate


@strawberry.type
class CertificateQuery:
    """Certificate queries."""

    @strawberry_django.field
    def certificate(self, certificate_id: str) -> CertificateNode | None:
        """Resolve certificate by raw ID."""
        try:
            return Certificate.objects.select_related(
                "github_user",
            ).get(id=certificate_id)
        except (Certificate.DoesNotExist, ValidationError, ValueError):
            return None

    @strawberry_django.field(permission_classes=[IsAuthenticated])
    def my_certificates(self, info: strawberry.types.Info) -> list[CertificateNode]:
        """Resolve current authenticated user's certificates."""
        user = info.context.request.user
        if getattr(user, "github_user", None) is None:
            return []

        return (
            Certificate.objects.select_related(
                "github_user",
            )
            .filter(github_user=user.github_user, is_revoked=False)
            .order_by("-issued_at")
        )
