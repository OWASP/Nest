"""Module model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.common.utils import slugify
from apps.mentorship.models.common import (
    ExperienceLevel,
    MatchingAttributes,
    StartEndRange,
)
from apps.mentorship.models.managers import PublishedModuleManager


class Module(ExperienceLevel, MatchingAttributes, StartEndRange, TimestampedModel):
    """Module model representing a program unit."""

    objects = models.Manager()
    published_modules = PublishedModuleManager()

    class Meta:
        db_table = "mentorship_modules"
        verbose_name_plural = "Modules"
        constraints = [
            models.UniqueConstraint(
                fields=["program", "key"],
                name="unique_module_key_in_program",
            )
        ]

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )

    key = models.CharField(
        verbose_name="Key",
        max_length=200,
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        blank=True,
        default="",
    )

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

    labels = models.JSONField(
        blank=True,
        default=list,
        verbose_name="Labels",
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
            self.started_at = self.started_at or self.program.started_at
            self.ended_at = self.ended_at or self.program.ended_at

        self.key = slugify(self.name)
        super().save(*args, **kwargs)
