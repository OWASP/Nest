"""Mentee model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes


class Mentee(ExperienceLevel, MatchingAttributes, TimestampedModel):
    """Mentee model."""

    class Meta:
        db_table = "mentorship_mentees"
        verbose_name_plural = "Mentees"

    # FKs.
    github_user = models.OneToOneField(
        "github.User",
        on_delete=models.CASCADE,
        verbose_name="GitHub user",
    )

    nest_user = models.OneToOneField(
        "nest.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
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
        return self.github_user.login
