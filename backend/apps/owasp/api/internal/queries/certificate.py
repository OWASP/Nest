"""OWASP certificate GraphQL queries."""

import uuid

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
    def certificate(self, certificate_id: uuid.UUID) -> CertificateNode | None:
        """Resolve certificate by raw UUID."""
        try:
            return Certificate.objects.select_related(
                "github_user",
                "github_user__contribution_score",
            ).get(id=certificate_id)
        except (Certificate.DoesNotExist, ValidationError, ValueError):
            return None

    @strawberry.field(permission_classes=[IsAuthenticated])
    def my_certificate(self, info: strawberry.types.Info) -> CertificateNode | None:
        """Resolve current authenticated user's latest certificate."""
        user = info.context.request.user
        if getattr(user, "github_user", None) is None:
            return None

        return (
            Certificate.objects.select_related(
                "github_user",
                "github_user__contribution_score",
            )
            .filter(github_user=user.github_user, is_revoked=False)
            .order_by("-issued_at")
            .first()
        )
