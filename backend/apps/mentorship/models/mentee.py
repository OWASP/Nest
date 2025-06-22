"""Mentee model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes
from apps.nest.models import User


class Mentee(TimestampedModel, ExperienceLevel, MatchingAttributes):
    """Mentee model."""

    class Meta:
        db_table = "mentorship_mentees"
        verbose_name_plural = "Mentees"

    # FKs.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="mentee",
        verbose_name="Nest user",
    )

    # M2Ms.
    programs = models.ManyToManyField(
        "mentorship.Program",
        through="mentorship.MenteeProgram",
        related_name="mentees",
        verbose_name="Enrolled programs",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the mentee.

        Returns:
            str: The GitHub username of the mentee.

        """
        return self.user.login if self.user else "Unlinked Mentee"
