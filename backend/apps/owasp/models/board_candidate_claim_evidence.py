"""OWASP app Board Candidate Claim Evidence model."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


class BoardCandidateClaimEvidence(TimestampedModel):
    """Model representing a Board Candidate Claim Evidence."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_candidate_claim_evidence"
        indexes = [
            models.Index(fields=["claim", "is_removed"], name="owasp_evidence_claim_active"),
        ]
        verbose_name_plural = "Board Candidate Claim Evidences"

    claim = models.ForeignKey(
        BoardCandidateClaim, on_delete=models.CASCADE, related_name="evidences"
    )
    description = models.TextField(default="", verbose_name="Description")
    file = models.FileField(
        blank=True, null=True, upload_to="bod/claim/evidence/", verbose_name="File"
    )
    file_name = models.CharField(
        blank=True,
        max_length=1000,
        verbose_name="File Name",
    )
    file_size = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="File Size (Bytes)"
    )
    is_removed = models.BooleanField(
        default=False,
        help_text="Indicates if the file is removed",
        verbose_name="Is removed",
    )
    key = models.CharField(max_length=100, unique=True, verbose_name="Key")
    name = models.CharField(max_length=1000, verbose_name="Name")
    removed_at = models.DateTimeField(blank=True, null=True)
    removed_reason = models.TextField(blank=True)
    source_url = models.TextField(blank=True, verbose_name="Source URL")

    def __str__(self):
        """Return a string representation of the a Board Candidate Claim Evidence."""
        return f"{self.name}"

    def clean(self) -> None:
        """Validate evidence."""
        super().clean()

        if (
            self.claim_id
            and BoardCandidateClaim.objects.filter(
                pk=self.claim_id,
                is_locked=True,
            ).exists()
        ):
            err = "Cannot add or modify evidence on a locked claim."
            raise ValidationError(err)

        if not (self.file or self.source_url):
            err = "Either file or source_url is required."
            raise ValidationError(err)

        if self.file:
            if not self.file_name:
                self.file_name = self.file.name
            if not self.file_size:
                self.file_size = self.file.size

    def save(self, *args, **kwargs) -> None:
        """Save evidence."""
        self.full_clean()
        super().save(*args, **kwargs)
