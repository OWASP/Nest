"""Module model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentor import Mentor
from apps.owasp.models.project import Project


class Module(TimestampedModel):
    """Module model representing a specific contribution unit within a program."""

    class Meta:
        db_table = "mentorship_modules"
        verbose_name_plural = "Modules"

    # foreign_key
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="Associated project",
    )
    # M2M
    mentors = models.ManyToManyField(
        Mentor,
        related_name="modules",
        verbose_name="Mentors",
        blank=True,
    )

    mentees = models.ManyToManyField(
        Mentee,
        related_name="modules",
        verbose_name="Mentees",
        blank=True,
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Module name",
        blank=True,
        default="",
    )

    description = models.TextField(
        verbose_name="Module description",
        blank=True,
        default="",
    )

    start_date = models.DateField(
        verbose_name="Start date",
    )

    end_date = models.DateField(
        verbose_name="End date",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the module.

        Returns:
            str: The module name or associated project.

        """
        return self.name or f"Module for {self.project.name}"
