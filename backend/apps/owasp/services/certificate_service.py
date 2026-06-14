"""Certificate service layer for Contributor Recognition Program."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from apps.owasp.models.crp.certificate import Certificate
from apps.owasp.services.certificate_providers import CertificateProviderFactory

if TYPE_CHECKING:
    from apps.github.models.user import User
    from apps.owasp.models.crp.recognition_enums import TierChoices

logger = logging.getLogger(__name__)


class CertificateService:
    """Service layer for orchestrating contributor certificate workflows."""

    @classmethod
    def issue_certificate(cls, user: User, score: int, tier: TierChoices) -> None:
        """Issue the certificate for the user's current tier if it does not already exist.

        Args:
            user (User): The user to issue certificates for.
            score (int): The current contribution score of the user.
            tier (TierChoices): The current tier the user qualifies for.

        """
        # Check if user already has an active certificate for this specific tier
        has_active_cert = Certificate.objects.filter(
            github_user=user,
            tier=tier,
            is_revoked=False,
        ).exists()

        if has_active_cert:
            return

        try:
            provider = CertificateProviderFactory.get_provider()
        except ValueError:
            logger.exception("Failed to resolve certificate provider")
            return

        logger.info(
            "Issuing %s certificate to user %s with score %s",
            tier,
            user.login,
            score,
        )
        try:
            provider.issue(user, score, tier)
        except Exception:
            logger.exception(
                "Failed to issue %s certificate for user %s",
                tier,
                user.login,
            )
