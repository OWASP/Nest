"""TaskLevel model for the Mentorship app."""

from __future__ import annotations

from django.db import models


class TaskLevel(models.Model):
    """Task level model representing difficulty and prerequisites for mentorship tasks."""

    class Meta:
        """Model options."""

        db_table = "mentorship_task_levels"
        verbose_name_plural = "Task Levels"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["module", "name"], name="unique_module_tasklevel_name")
        ]

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )

    labels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Labels",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        default="",
    )

    # FKs.
    module = models.ForeignKey(
        "mentorship.Module",
        on_delete=models.CASCADE,
        related_name="task_levels",
        verbose_name="Module",
    )

    # M2Ms.
    needs = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="required_by",
        verbose_name="Prerequisite Levels",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the task level.

        Returns:
            str: Module name with task level name.

        """
        return f"{self.module.name} - {self.name}"
