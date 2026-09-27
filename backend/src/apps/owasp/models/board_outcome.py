"""OWASP app board outcome model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.entity_member import EntityMember


class BoardOutcome(TimestampedModel):
    """Board outcome model."""

    class Status(models.TextChoices):
        """Board outcome status choices."""

        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        IN_PROGRESS = "in_progress", "In Progress"
        PENDING = "pending", "Pending"

    class Meta:
        """Model options."""

        db_table = "owasp_board_outcomes"
        verbose_name_plural = "Board Outcomes"

    description = models.TextField()
    due_date = models.DateField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.PENDING,
    )

    assignees = models.ManyToManyField(
        EntityMember,
        blank=True,
        related_name="+",
    )

    def __str__(self) -> str:
        """Return the board outcome human-readable representation."""
        return f"Outcome ({self.get_status_display()}): {self.description[:60]}"
