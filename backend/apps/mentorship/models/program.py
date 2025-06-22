"""Program model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import ExperienceLevel


class Program(TimestampedModel, ExperienceLevel):
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

    end_date = models.DateField(verbose_name="End date")

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

    start_date = models.DateField(verbose_name="Start date")

    status = models.CharField(
        verbose_name="Status",
        max_length=9,
        choices=ProgramStatus.choices,
        default=ProgramStatus.DRAFT,
    )

    # M2Ms.
    modules = models.ManyToManyField(
        "mentorship.Module",
        through="mentorship.ProgramModule",
        related_name="programs",
        verbose_name="Modules",
        blank=True,
    )

    owners = models.ManyToManyField(
        "mentorship.Mentor",
        related_name="owned_programs",
        verbose_name="Owners",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the program.

        Returns:
            str: The program name.

        """
        return self.name
