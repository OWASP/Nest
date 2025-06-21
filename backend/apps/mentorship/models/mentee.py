"""Mentee model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models import User


class Mentee(TimestampedModel):
    """Mentee model."""

    class Meta:
        db_table = "mentorship_mentees"
        verbose_name_plural = "Mentees"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="mentee",
        verbose_name="GitHub user",
    )

    programs = models.ManyToManyField(
        "Program",
        through="mentorship.Enrollment",
        related_name="mentees",
        verbose_name="Enrolled programs",
        blank=True,
    )

    tags = models.JSONField(
        verbose_name="Technology tags (e.g., languages, frameworks)",
        default=list,
        blank=True,
    )

    domains = models.JSONField(
        verbose_name="Relevant domains or topics",
        default=list,
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the mentee.

        Returns:
            str: The GitHub username of the mentee.

        """
        return self.user.login if self.user else "Unlinked Mentee"
