"""Module model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import (
    ExperienceLevel,
    MatchingAttributes,
    StartEndRange,
)


class Module(ExperienceLevel, MatchingAttributes, StartEndRange, TimestampedModel):
    """Module model representing a program unit."""

    class Meta:
        db_table = "mentorship_modules"
        verbose_name_plural = "Modules"

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        blank=True,
        default="",
    )
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)

    # FKs.
    program = models.ForeignKey(
        "mentorship.Program",
        related_name="modules",
        on_delete=models.CASCADE,
        verbose_name="Program",
    )

    project = models.ForeignKey(
        "owasp.Project",
        on_delete=models.CASCADE,
        verbose_name="Project",
    )

    # M2Ms.
    mentors = models.ManyToManyField(
        "mentorship.Mentor",
        verbose_name="Mentors",
        related_name="modules",
        through="mentorship.MentorModule",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the module.

        Returns:
            str: The module name or associated project.

        """
        return self.name

    def save(self, *args, **kwargs):
        """Save module."""
        if self.program:
            # Set default dates from program if not provided.
            self.started_at = self.started_at or self.program.started_at
            self.ended_at = self.ended_at or self.program.ended_at

        super().save(*args, **kwargs)
