"""Certificate model for tracking contributor achievements."""

from __future__ import annotations

import logging
import secrets

from django.db import models, transaction
from django.db.models import Q

from apps.common.models import TimestampedModel
from apps.github.models.user import User
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.recognition_enums import TierChoices
from apps.owasp.utils.certificate_provider import CertificateProviderFactory

logger = logging.getLogger(__name__)

CERTIFICATE_ID_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CERTIFICATE_ID_LENGTH = 12


def generate_certificate_id() -> str:
    """Generate a unique 12-character alphanumeric ID for certificates."""
    return "".join(secrets.choice(CERTIFICATE_ID_ALPHABET) for _ in range(CERTIFICATE_ID_LENGTH))


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
                fields=["recipient", "tier"],
                condition=Q(is_revoked=False) & ~Q(tier=""),
                name="unique_active_cert_per_tier",
                violation_error_message="Cannot have multiple active certificates for same tier",
            ),
            models.CheckConstraint(
                condition=(
                    Q(tier__in=TierChoices.values)
                    | (
                        ~Q(title="")
                        & Q(title__isnull=False)
                        & (
                            (Q(project__isnull=False) & Q(chapter__isnull=True))
                            | (Q(project__isnull=True) & Q(chapter__isnull=False))
                        )
                    )
                ),
                name="valid_certificate_type",
                violation_error_message=(
                    "Certificate must be either a valid tier certificate or a generic certificate"
                    " with a title and associated project/chapter."
                ),
            ),
        ]

    id = models.CharField(
        primary_key=True,
        default=generate_certificate_id,
        max_length=12,
        editable=False,
        verbose_name="Certificate ID",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificates",
        help_text="Recipient GitHub user",
    )
    issuer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="issued_certificates",
        blank=True,
        null=True,
        help_text="Issuer GitHub user (for generic certificates)",
    )
    title = models.CharField(
        verbose_name="Title",
        max_length=255,
        blank=True,
        default="",
        help_text="Certificate title",
    )
    message = models.TextField(
        verbose_name="Message",
        blank=True,
        default="",
        help_text="Customizable certificate message",
    )
    project = models.ForeignKey(
        "owasp.Project",
        on_delete=models.SET_NULL,
        related_name="certificates",
        blank=True,
        null=True,
        help_text="Associated project",
    )
    chapter = models.ForeignKey(
        "owasp.Chapter",
        on_delete=models.SET_NULL,
        related_name="certificates",
        blank=True,
        null=True,
        help_text="Associated chapter",
    )
    tier = models.CharField(
        verbose_name="Tier",
        max_length=20,
        choices=TierChoices.choices,
        blank=True,
        default="",
        help_text="The tier at which the certificate was issued",
    )
    score = models.PositiveIntegerField(
        verbose_name="Score",
        blank=True,
        null=True,
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

    @property
    def is_verified(self) -> bool:
        """Return whether the certificate is active/verified (not revoked)."""
        return not self.is_revoked

    def __str__(self) -> str:
        """Return human-readable representation."""
        status = "Revoked" if self.is_revoked else "Active"
        cert_type = self.title or (
            f"{self.tier.upper()} Certificate" if self.tier else "Certificate"
        )
        recipient_name = self.recipient.login if self.recipient else "No Recipient"
        return f"{recipient_name} - {cert_type} ({status})"

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
            recipient=user,
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
