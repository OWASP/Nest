"""Certificate model for tracking contributor achievements."""

from __future__ import annotations

import logging
import secrets

from django.db import models, transaction
from django.db.models import Q

from apps.common.models import TimestampedModel
from apps.github.models.user import User
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.certificate_provider import CertificateProviderFactory
from apps.owasp.models.crp.recognition_enums import TierChoices


logger = logging.getLogger(__name__)

CERTIFICATE_ID_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CERTIFICATE_ID_LENGTH = 12


def generate_certificate_id() -> str:
    """Generate a unique 12-character alphanumeric ID for certificates."""
    return "".join(
        secrets.choice(CERTIFICATE_ID_ALPHABET) for _ in range(CERTIFICATE_ID_LENGTH)
    )


class Certificate(TimestampedModel):
    """Certificate model.

    Tracks contributor certificate metadata issued at tier milestones.
    Certificates are dynamically generated during download using stored metadata.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_crp_certificates"
        verbose_name_plural = "Certificates"
        indexes = [
            models.Index(fields=["-issued_at"], name="cert_issued_at_desc"),
            models.Index(fields=["tier"], name="cert_tier_idx"),
            models.Index(fields=["is_revoked"], name="cert_revoked_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["github_user", "tier"],
                condition=Q(is_revoked=False),
                name="unique_active_cert_per_tier",
                violation_error_message="Cannot have multiple active certificates for same tier",
            ),
        ]

    id = models.CharField(
        primary_key=True,
        default=generate_certificate_id,
        max_length=12,
        editable=False,
        verbose_name="Certificate ID",
    )
    github_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificates",
        help_text="Associated GitHub user",
    )
    tier = models.CharField(
        verbose_name="Tier",
        max_length=20,
        choices=TierChoices.choices,
        help_text="The tier at which the certificate was issued",
    )
    score = models.PositiveIntegerField(
        verbose_name="Score",
        help_text="The contributor's score when the certificate was issued",
    )
    issued_at = models.DateTimeField(
        verbose_name="Issued At",
        auto_now_add=True,
        help_text="Timestamp when the certificate was issued",
    )
    is_revoked = models.BooleanField(
        verbose_name="Is Revoked",
        default=False,
        help_text="Whether the certificate has been revoked",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        status = "Revoked" if self.is_revoked else "Active"
        return f"{self.github_user.login} - {self.tier.upper()} Certificate ({status})"

    @classmethod
    @transaction.atomic
    def issue_certificate(cls, user: User, score: int, tier: TierChoices) -> None:
        """Issue a certificate for the user's current tier if one does not already exist.

        Locks the User row to serialize concurrent issuances, checks for an existing
        active certificate at this tier, and delegates to the configured provider.

        Args:
            user (User): The user to issue a certificate for.
            score (int): The current contribution score of the user.
            tier (TierChoices): The tier the user qualifies for.

        Raises:
            CertificateIssuanceError: If provider resolution or issuance fails.

        """
        # Lock the User row to serialize concurrent certificate issuances for this user
        user = User.objects.select_for_update().get(id=user.id)

        # Check if user already has an active certificate for this specific tier
        if cls.objects.filter(
            github_user=user,
            tier=tier,
            is_revoked=False,
        ).exists():
            return

        try:
            provider = CertificateProviderFactory.get_provider()
        except ValueError as e:
            logger.exception("Failed to resolve certificate provider")
            raise CertificateIssuanceError from e

        logger.info(
            "Issuing %s certificate to user %s with score %s",
            tier,
            user.login,
            score,
        )
        try:
            provider.issue_certificate(user, score, tier)
        except Exception as e:
            logger.exception(
                "Failed to issue %s certificate for user %s",
                tier,
                user.login,
            )
            raise CertificateIssuanceError from e
