"""Enrollment model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes


class MenteeModule(TimestampedModel, ExperienceLevel, MatchingAttributes):
    """Mentee program enrollment."""

    class Meta:
        db_table = "mentorship_mentee_modules"
        verbose_name_plural = "Mentee modules"
        unique_together = ("mentee", "module")

    # FKs.
    mentee = models.ForeignKey(
        "mentorship.Mentee",
        on_delete=models.CASCADE,
        verbose_name="Mentee",
    )

    module = models.ForeignKey(
        "mentorship.Module",
        on_delete=models.CASCADE,
        verbose_name="Module",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the enrollment.

        Returns:
            str: Mentee and program with level.

        """
        return f"{self.mentee} - {self.module}"
