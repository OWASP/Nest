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

    class Meta:
        db_table = "owasp_badges"
        indexes = [
            models.Index(fields=["-created_at"], name="badge_created_at_desc_idx"),
            models.Index(fields=["-updated_at"], name="badge_updated_at_desc_idx"),
        ]
        verbose_name_plural = "Badges"

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
    created_at = models.DateTimeField(verbose_name="Created at", blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name="Updated at", blank=True, null=True)

    def __str__(self) -> str:
        """Return the badge name as its string representation."""
        return self.name

    @property
    def badge_name(self) -> str:
        """Return the badge name."""
        return self.name

    @property
    def badge_description(self) -> str:
        """Return the badge description."""
        return self.description

    @property
    def badge_css_class(self) -> str:
        """Return the badge CSS class."""
        return self.css_class

    @property
    def badge_weight(self) -> int:
        """Return the badge weight."""
        return self.weight

    @property
    def badge_created_at(self) -> str:
        """Return the badge creation timestamp."""
        return self.created_at

    @property
    def badge_updated_at(self) -> str:
        """Return the badge last updated timestamp."""
        return self.updated_at

    ordering = ["weight", "name"]
