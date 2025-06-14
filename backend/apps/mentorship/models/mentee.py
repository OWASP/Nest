"""Mentee model for the Mentorship app."""

from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
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

    level = models.PositiveIntegerField(
        verbose_name="Mentee level",
    )

    top_skills = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        verbose_name="Top skills (languages/frameworks)",
    )

    preferred_tech_stack = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        verbose_name="Preferred tech stack",
    )

    interested_domains = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        verbose_name="Interested domains",
    )

    issues_worked_on = models.PositiveIntegerField(
        verbose_name="Number of issues worked on",
        default=0,
    )

    prs_opened = models.PositiveIntegerField(
        verbose_name="Number of PRs opened",
        default=0,
    )

    prs_merged = models.PositiveIntegerField(
        verbose_name="Number of PRs merged",
        default=0,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the mentee.

        Returns:
            str: The GitHub username of the mentee.

        """
        return self.user.login if self.user else "Unlinked Mentee"
