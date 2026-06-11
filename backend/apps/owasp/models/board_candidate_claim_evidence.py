"""OWASP app Board Candidate Claim Evidence model."""

from __future__ import annotations

import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files import storage
from django.db import models

from apps.common.models import TimestampedModel
from apps.common.utils import slugify
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.validators import (
    validate_evidence_extension,
    validate_evidence_file_size,
)


def uuid_upload_to(_instance, filename):
    """Return path with generated UUID."""
    return f"bod/claim/evidence/{uuid.uuid4()}{Path(filename).suffix}"


class BoardCandidateClaimEvidence(TimestampedModel):
    """Model representing a Board Candidate Claim Evidence."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_candidate_claim_evidence"
        constraints = [
            models.UniqueConstraint(
                fields=["claim", "key"], name="owasp_evidence_claim_key_unique"
            ),
            models.UniqueConstraint(
                fields=["claim", "name"], name="owasp_evidence_claim_name_unique"
            ),
        ]
        indexes = [
            models.Index(fields=["claim", "is_removed"], name="owasp_evidence_claim_active"),
        ]
        verbose_name_plural = "Board Candidate Claim Evidences"

    REMOVAL_ALLOWED_STATUSES = frozenset(
        {
            BoardCandidateClaim.Status.DISCARDED,
            BoardCandidateClaim.Status.DRAFT,
            BoardCandidateClaim.Status.WITHDRAWN,
        }
    )

    claim = models.ForeignKey(
        BoardCandidateClaim, on_delete=models.CASCADE, related_name="evidences"
    )
    description = models.TextField(default="", verbose_name="Description")
    file = models.FileField(
        blank=True,
        null=True,
        upload_to=uuid_upload_to,
        validators=[
            validate_evidence_extension,
            validate_evidence_file_size,
        ],
        verbose_name="File",
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
    name = models.CharField(
        max_length=200,
        verbose_name="Name",
    )
    key = models.CharField(verbose_name="Key", max_length=100)
    removed_at = models.DateTimeField(blank=True, null=True)
    removed_reason = models.TextField(blank=True)
    source_url = models.TextField(blank=True, verbose_name="Source URL")

    def __str__(self):
        """Return a string representation of the a Board Candidate Claim Evidence."""
        return f"{self.name}"

    def clean(self) -> None:
        """Validate evidence."""
        super().clean()

        if not (self.file or self.source_url):
            err = "Either file or source_url is required."
            raise ValidationError(err)

        if self.claim_id:
            claim_status = (
                BoardCandidateClaim.objects.values_list("status", flat=True)
                .filter(pk=self.claim_id)
                .first()
            )

            if claim_status is None:
                err = "Claim does not exist."
                raise ValidationError(err)

            if self.is_removed and claim_status not in self.REMOVAL_ALLOWED_STATUSES:
                err = "Can only remove evidence from discarded, draft or withdrawn claim."
                raise ValidationError(err)

            if not self.is_removed and claim_status != BoardCandidateClaim.Status.DRAFT:
                err = "Cannot add or modify evidence on a non-draft claim."
                raise ValidationError(err)

        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size

    def save(self, *args, **kwargs) -> None:
        """Save evidence."""
        self.key = slugify(self.name)

        self.full_clean()

        super().save(*args, **kwargs)
        if self.pk and self.file:
            old_file = (
                self.__class__.objects.filter(pk=self.pk).values_list("file", flat=True).first()
            )
            if old_file and old_file != self.file.name:
                storage.default_storage.delete(old_file)
