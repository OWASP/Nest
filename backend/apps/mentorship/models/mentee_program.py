"""Enrollment model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes


class MenteeProgram(TimestampedModel, ExperienceLevel, MatchingAttributes):
    """Mentee program enrollment."""

    class Meta:
        db_table = "mentorship_mentee_programs"
        verbose_name_plural = "Mentee programs"
        unique_together = ("mentee", "program")

    # FKs.
    mentee = models.ForeignKey(
        "Mentee",
        on_delete=models.CASCADE,
        verbose_name="Mentee",
    )

    program = models.ForeignKey(
        "Program",
        on_delete=models.CASCADE,
        verbose_name="Program",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the enrollment.

        Returns:
            str: Mentee and program with level.

        """
        return f"{self.mentee} - {self.program}"
