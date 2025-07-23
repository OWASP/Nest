"""Task model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import Status


class Task(Status, TimestampedModel):
    """Connects a Module, a GitHub Issue, and a Mentee to track work."""

    class Meta:
        db_table = "mentorship_tasks"
        verbose_name_plural = "Tasks"
        unique_together = ("issue", "assignee")
        ordering = ["deadline_at"]

    # FKs.
    assignee = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text="The mentee assigned to this task.",
    )

    issue = models.ForeignKey(
        "github.Issue",
        on_delete=models.PROTECT,
        related_name="mentorship_tasks",
        help_text="The GitHub issue this task corresponds to.",
    )

    module = models.ForeignKey(
        "mentorship.Module",
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="The module this task is part of.",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the task was assigned to the mentee.",
    )

    deadline_at = models.DateTimeField(
        null=True, blank=True, help_text="Optional deadline for the task."
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional data",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the task."""
        return (
            f"Task for '{self.issue.title}' assigned to {self.assignee.login}"
            if self.assignee
            else f"Task: {self.issue.title} (Unassigned)"
        )
