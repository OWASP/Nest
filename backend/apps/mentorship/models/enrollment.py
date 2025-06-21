"""Enrollment model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.mentorship.models.common import MenteeLevelChoices
from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.program import Program


class Enrollment(models.Model):
    """Through model for Mentee-Program relationship with skill level."""

    class Meta:
        db_table = "mentorship_enrollments"
        verbose_name_plural = "Enrollments"
        unique_together = ["mentee", "program"]

    mentee = models.ForeignKey(
        Mentee,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Mentee",
    )

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Program",
    )

    level = models.CharField(
        max_length=20,
        choices=MenteeLevelChoices.choices,
        default=MenteeLevelChoices.BEGINNER,
        verbose_name="Skill level in this program",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the enrollment.

        Returns:
            str: Mentee and program with level.

        """
        return f"{self.mentee} - {self.program} ({self.level})"
