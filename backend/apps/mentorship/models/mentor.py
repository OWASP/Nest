"""Mentor model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel, MatchingAttributes


class Mentor(ExperienceLevel, MatchingAttributes, TimestampedModel):
    """Mentor model."""

    class Meta:
        """Model options."""

        db_table = "mentorship_mentors"
        verbose_name_plural = "Mentors"

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

    def __str__(self) -> str:
        """Return a human-readable representation of the mentor.

        Returns:
            str: The GitHub username of the mentor.

        """
        return self.github_user.login
