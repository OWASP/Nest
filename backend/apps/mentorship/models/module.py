"""Module model for the Mentorship app."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel


class Module(TimestampedModel):
    """Module model representing a program unit."""

    class Meta:
        db_table = "mentorship_modules"
        verbose_name_plural = "Modules"

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        default="",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        blank=True,
        default="",
    )

    # FKs.
    project = models.ForeignKey(
        "owasp.Project",
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="Project",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the module.

        Returns:
            str: The module name or associated project.

        """
        return self.name
