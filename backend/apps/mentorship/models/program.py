"""Program model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import MenteeLevelChoices
from apps.mentorship.models.mentor import Mentor


class Program(TimestampedModel):
    """Program model representing an overarching mentorship initiative."""

    class Meta:
        db_table = "mentorship_programs"
        verbose_name_plural = "Programs"

    class ProgramStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        COMPLETED = "completed", "Completed"

    name = models.CharField(
        max_length=200,
        verbose_name="Program name",
    )

    description = models.TextField(
        verbose_name="Program description",
        blank=True,
        default="",
    )

    preferred_mentee_level = models.CharField(
        max_length=20,
        choices=MenteeLevelChoices.choices,
        default=MenteeLevelChoices.BEGINNER,
        verbose_name="Skill level in this program",
    )

    mentee_limit = models.PositiveIntegerField(
        verbose_name="Mentee limit",
        default=1,
        help_text="Maximum number of mentees allowed in this program",
    )

    active_mentees = models.PositiveIntegerField(
        verbose_name="Active mentees",
        default=0,
        help_text="Current number of active mentees enrolled",
    )

    is_available = models.BooleanField(
        verbose_name="Currently available",
        default=True,
        help_text="Whether this program is currently accepting new mentees",
    )
    # M2M
    owners = models.ManyToManyField(
        Mentor,
        related_name="owned_programs",
        verbose_name="Program owners",
        blank=True,
    )
    modules = models.ManyToManyField(
        "Module",
        through="mentorship.ProgramModule",
        related_name="linked_programs",
        verbose_name="Modules",
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

    status = models.CharField(
        verbose_name="Program status",
        max_length=20,
        choices=ProgramStatus.choices,
        default=ProgramStatus.DRAFT,
    )

    start_date = models.DateField(
        verbose_name="Start date",
    )

    end_date = models.DateField(
        verbose_name="End date",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the program.

        Returns:
            str: The program name.

        """
        return self.name
