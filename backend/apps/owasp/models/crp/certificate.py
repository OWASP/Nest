"""Certificate model for tracking contributor achievements."""

from __future__ import annotations

import uuid

from django.db import models
from django.db.models import Q

from apps.common.models import TimestampedModel
from apps.github.models.user import User
from apps.owasp.models.crp.recognition_enums import TierChoices


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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
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
