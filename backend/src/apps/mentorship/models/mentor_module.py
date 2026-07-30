"""ProgramModule model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes


class MentorModule(ExperienceLevel, MatchingAttributes, TimestampedModel):
    """Mentor module model."""

    class Meta:
        """Model options."""

        db_table = "mentorship_mentor_modules"
        unique_together = ("mentor", "module")
        verbose_name = "Mentor module"
        verbose_name_plural = "Mentor modules"

    role = models.CharField(
        max_length=100,
        verbose_name="Role",
        blank=True,
        default="Mentor",
    )

    # FKs.
    mentor = models.ForeignKey(
        "mentorship.Mentor",
        on_delete=models.CASCADE,
        verbose_name="Program",
    )

    module = models.ForeignKey(
        "mentorship.Module",
        on_delete=models.CASCADE,
        verbose_name="Module",
    )

    def __str__(self) -> str:
        """Return a readable identifier for the mentor module link."""
        return f"{self.mentor} of {self.module}"
