"""Program model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.models.module import Module


class Program(TimestampedModel):
    """Program model representing an overarching mentorship initiative."""

    class Meta:
        db_table = "mentorship_programs"
        verbose_name_plural = "Programs"

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("completed", "Completed"),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="Program name",
    )

    description = models.TextField(
        verbose_name="Program description",
        blank=True,
        default="",
    )
    # M2M
    owners = models.ManyToManyField(
        Mentor,
        related_name="owned_programs",
        verbose_name="Program owners",
        blank=True,
    )
    modules = models.ManyToManyField(
        Module,
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
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Program status",
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
