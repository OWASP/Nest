"""OWASP app Board Candidate Claim model."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class BoardCandidateClaim(TimestampedModel):
    """Model representing a Board Candidate Claim."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_candidate_claim"
        indexes = [
            models.Index(fields=["candidate", "status"], name="owasp_claim_candidate_status"),
            models.Index(fields=["board", "status"], name="owasp_claim_board_status"),
        ]
        verbose_name_plural = "Board Candidate Claims"

    class Status(models.TextChoices):
        """Status choices."""

        APPROVED = "APPROVED", "Approved"
        DISCARDED = "DISCARDED", "Discarded"
        DRAFT = "DRAFT", "Draft"
        REJECTED = "REJECTED", "Rejected"
        SUBMITTED = "SUBMITTED", "Submitted"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    FINALIZED_STATUSES = {Status.APPROVED, Status.DISCARDED, Status.REJECTED, Status.WITHDRAWN}
    VALID_TRANSITIONS = {
        Status.DRAFT: {Status.SUBMITTED, Status.DISCARDED},
        Status.SUBMITTED: {Status.APPROVED, Status.REJECTED, Status.WITHDRAWN},
        Status.APPROVED: {Status.WITHDRAWN},
        Status.REJECTED: set(),
        Status.DISCARDED: set(),
        Status.WITHDRAWN: set(),
    }
    WITHDRAWAL_ALLOWED_FIELDS = frozenset({"status", "withdrawn_reason", "withdrawn_at"})

    board = models.ForeignKey(
        BoardOfDirectors, blank=True, null=True, on_delete=models.SET_NULL, related_name="claims"
    )
    candidate = models.ForeignKey(EntityMember, on_delete=models.CASCADE, related_name="claims")
    description = models.TextField(default="", verbose_name="Description")
    is_locked = models.BooleanField(
        default=False,
        help_text="Indicates if the claim is locked",
        verbose_name="Is locked",
    )
    status = models.CharField(
        choices=Status.choices,
        default=Status.DRAFT,
        max_length=20,
        verbose_name="Claim status",
    )
    title = models.CharField(max_length=1000, verbose_name="Title")
    withdrawn_at = models.DateTimeField(blank=True, null=True)
    withdrawn_reason = models.TextField(blank=True)

    def __str__(self):
        """Return a string representation of the a Board Candidate Claim."""
        return f"{self.title}"

    def clean(self) -> None:
        """Validate claim."""
        super().clean()
        if not self.pk:
            if self.status != self.Status.DRAFT:
                error_message = "New claims must be created as draft."
                raise ValidationError(error_message)
            return

        existing_claim = BoardCandidateClaim.objects.filter(
            pk=self.pk,
        ).first()

        if not existing_claim:
            error_message = "Claim does not exist."
            raise ValidationError(error_message)

        if self.status != existing_claim.status and self.status not in self.VALID_TRANSITIONS.get(
            existing_claim.status, set()
        ):
            error_message = (
                f"Invalid status transition from {existing_claim.status} to {self.status}."
            )
            raise ValidationError(error_message)

        if self.status == self.Status.WITHDRAWN and any(
            f.attname not in self.WITHDRAWAL_ALLOWED_FIELDS
            for f in self._meta.fields
            if getattr(self, f.attname) != getattr(existing_claim, f.attname)
        ):
            error_message = "Cannot update fields while withdrawing a claim."
            raise ValidationError(error_message)

        if (
            self.status != self.Status.WITHDRAWN
            and existing_claim.status != self.Status.DRAFT
            and any(
                f.attname != "status"
                for f in self._meta.fields
                if getattr(self, f.attname) != getattr(existing_claim, f.attname)
            )
        ):
            error_message = "Can only update status on a non-draft claim"
            raise ValidationError(error_message)

    def save(self, *args, **kwargs) -> None:
        """Save claim."""
        self.full_clean()

        if self.status in self.FINALIZED_STATUSES:
            self.is_locked = True

        super().save(*args, **kwargs)
