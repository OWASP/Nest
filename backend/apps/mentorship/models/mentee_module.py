"""Enrollment model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import StartEndRange


class MenteeModule(StartEndRange, TimestampedModel):
    """Mentee module enrollment."""

    class Meta:
        db_table = "mentorship_mentee_modules"
        verbose_name_plural = "Mentee modules"
        unique_together = ("mentee", "module")

    ended_at = models.DateTimeField(
        verbose_name="End date and time",
        blank=True,
        null=True,
    )

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
