"""Program model for the Mentorship app."""

from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.common.models import TimestampedModel
from apps.common.utils import slugify
from apps.mentorship.models.common import (
    ExperienceLevel,
    MatchingAttributes,
    StartEndRange,
)
from apps.mentorship.models.mixins.program import ProgramIndexMixin


class Program(MatchingAttributes, ProgramIndexMixin, StartEndRange, TimestampedModel):
    """Program model representing an overarching mentorship initiative."""

    class Meta:
        db_table = "mentorship_programs"
        verbose_name_plural = "Programs"

    class ProgramStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        COMPLETED = "completed", "Completed"

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )

    experience_levels = ArrayField(
        base_field=models.CharField(
            max_length=12,
            choices=ExperienceLevel.ExperienceLevelChoices.choices,
        ),
        blank=True,
        default=list,
        verbose_name="Experience levels",
    )

    mentees_limit = models.PositiveIntegerField(
        verbose_name="Mentees limit",
        blank=True,
        null=True,
        help_text="Maximum number of mentees allowed in this program",
    )

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Name",
    )
    key = models.CharField(verbose_name="Key", max_length=200, unique=True)

    status = models.CharField(
        verbose_name="Status",
        max_length=9,
        choices=ProgramStatus.choices,
        default=ProgramStatus.DRAFT,
    )

    # M2Ms.
    admins = models.ManyToManyField(
        "mentorship.Mentor",
        verbose_name="Admins",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the program.

        Returns:
            str: The program name.

        """
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save program."""
        self.key = slugify(self.name)

        super().save(*args, **kwargs)
