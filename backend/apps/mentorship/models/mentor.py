"""Mentor model for the Mentorship app."""

from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
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

    domain = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        verbose_name="Primary domain(s)",
    )

    preferred_mentee_level = models.PositiveIntegerField(
        verbose_name="Preferred mentee level",
        default=1,
    )

    mentee_limit = models.PositiveIntegerField(
        verbose_name="Mentee limit",
        default=1,
    )

    active_mentees = models.PositiveIntegerField(
        verbose_name="Active mentees",
        default=0,
    )

    is_available = models.BooleanField(
        verbose_name="Currently available",
        default=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the mentor.

        Returns:
            str: The GitHub username of the mentor.

        """
        return self.user.login

    @property
    def is_full(self) -> bool:
        """Check if the mentor has reached their mentee limit.

        Returns:
            bool: True if the mentor cannot take more mentees.

        """
        return self.active_mentees >= self.mentee_limit
