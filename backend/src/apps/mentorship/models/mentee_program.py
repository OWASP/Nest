"""Enrollment model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, StartEndRange


class MenteeProgram(ExperienceLevel, StartEndRange, TimestampedModel):
    """Mentee program enrollment."""

    class Meta:
        """Model options."""

        db_table = "mentorship_mentee_programs"
        verbose_name_plural = "Mentee programs"
        unique_together = ("mentee", "program")

    # FKs.
    mentee = models.ForeignKey(
        "mentorship.Mentee",
        on_delete=models.CASCADE,
        verbose_name="Mentee",
    )

    program = models.ForeignKey(
        "mentorship.Program",
        on_delete=models.CASCADE,
        verbose_name="Program",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the enrollment.

        Returns:
            str: Mentee and program with level.

        """
        return f"{self.mentee} - {self.program}"
