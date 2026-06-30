"""OWASP app Board Candidate Claim Review model."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimestampedModel
from apps.nest.models.user import User
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


class BoardCandidateClaimReview(TimestampedModel):
    """Model representing a Board Candidate Claim Review."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_candidate_claim_reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["claim", "reviewer"], name="owasp_claim_reviewer_unique"
            ),
        ]
        verbose_name_plural = "Board Candidate Claim Reviews"

    class Status(models.TextChoices):
        """Status choices."""

        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    claim = models.ForeignKey(
        BoardCandidateClaim, on_delete=models.CASCADE, related_name="reviews"
    )
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    status = models.CharField(
        choices=Status.choices,
        max_length=8,
        verbose_name="Review Status",
    )

    def __str__(self):
        """Return a string representation of the a Board Candidate Claim Review."""
        return (
            f"{self.claim.name} - "
            f"{
                self.reviewer.github_user.login
                if self.reviewer.github_user
                else self.reviewer.username
            }"
        )

    def clean(self) -> None:
        """Validate review."""
        super().clean()

        if not self.reviewer.github_user:
            err = "Reviewers must have a linked GitHub account."
            raise ValidationError(err)

        if self.claim.status != BoardCandidateClaim.Status.SUBMITTED:
            err = "Review can only be added to submitted claims."
            raise ValidationError(err)

        if (
            not self.claim.board
            or not self.claim.board.reviewers.filter(id=self.reviewer.id).exists()
        ):
            err = "Only Claim Reviewers can review claims."
            raise ValidationError(err)

        if self.claim.board and self.claim.board.get_candidate(
            login=self.reviewer.github_user.login
        ):
            err = "A candidate cannot review claims in the same election year."
            raise ValidationError(err)

    def save(self, *args, **kwargs) -> None:
        """Save review."""
        self.full_clean()
        super().save(*args, **kwargs)
