"""Mentorship app start/end range."""

from django.db import models


class Status(models.Model):
    """Defines the possible states of a task."""

    class Meta:
        abstract = True

    class StatusChoices(models.TextChoices):
        """Status choices."""

        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        IN_REVIEW = "IN_REVIEW", "In Review"
        COMPLETED = "COMPLETED", "Completed"

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.TODO,
        verbose_name="Task status",
    )
