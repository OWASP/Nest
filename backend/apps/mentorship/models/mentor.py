"""Mentor model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes
from apps.nest.models import User


class Mentor(TimestampedModel, ExperienceLevel, MatchingAttributes):
    """Mentor model."""

    class Meta:
        db_table = "mentorship_mentors"
        verbose_name_plural = "Mentors"

    # FKs.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="mentor",
        verbose_name="Nest user",
    )

    # M2Ms.
    modules = models.ManyToManyField(
        "mentorship.Module",
        through="mentorship.MentorModule",
        verbose_name="Modules",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the mentor.

        Returns:
            str: The GitHub username of the mentor.

        """
        return self.user.login if self.user else "Unlinked Mentor"
