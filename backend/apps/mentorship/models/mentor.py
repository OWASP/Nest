"""Mentor model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models import User


class Mentor(TimestampedModel):
    """Mentor model."""

    class Meta:
        db_table = "mentorship_mentors"
        verbose_name_plural = "Mentors"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="mentor",
        verbose_name="GitHub user",
    )

    years_of_experience = models.PositiveIntegerField(
        verbose_name="Years of experience",
        default=0,
    )

    domain = models.JSONField(
        default=list,
        verbose_name="Primary domain(s)",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the mentor.

        Returns:
            str: The GitHub username of the mentor.

        """
        return self.user.login if self.user else "Unlinked Mentor"
