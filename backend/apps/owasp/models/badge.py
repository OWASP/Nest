"""Badge model for OWASP Nest user achievements and roles."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class Badge(BulkSaveModel, TimestampedModel):
    """Represents a user badge for roles or achievements."""

    class Meta:
        db_table = "owasp_badges"
        ordering = ["weight", "name"]
        verbose_name_plural = "Badges"

    css_class = models.CharField(
        verbose_name="CSS Class",
        max_length=255,
        default="",
    )
    description = models.CharField(
        verbose_name="Description",
        max_length=255,
        blank=True,
        default="",
    )
    name = models.CharField(
        verbose_name="Name",
        max_length=255,
        unique=True,
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name="Weight",
        default=0,
    )

    def __str__(self) -> str:
        """Return the badge string representation."""
        return self.name
