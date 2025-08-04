"""Badge model for user achievements and roles in OWASP Nest."""

from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.models.common import RepositoryBasedEntityModel
from apps.owasp.models.mixins.project import ProjectIndexMixin


class Badge(BulkSaveModel, ProjectIndexMixin, RepositoryBasedEntityModel, TimestampedModel):
    """Represents a user badge for roles or achievements."""

    objects = models.Manager()

    name = models.CharField(max_length=255, unique=True, help_text="Name of the badge.")
    description = models.CharField(
        max_length=255, blank=True, help_text="A short description of the badge."
    )
    weight = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0)], help_text="A weight to sort badges by."
    )
    css_class = models.CharField(
        max_length=255, help_text="The font-awesome css class for the badge."
    )

    def __str__(self):
        """Return the badge name as its string representation."""
        return self.name

    class Meta:
        ordering = ["weight", "name"]
