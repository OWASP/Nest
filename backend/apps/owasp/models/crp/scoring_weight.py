"""Scoring weight model for OWASP contributor recognition."""

from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.crp.recognition_enums import EventTypeChoices


class ScoringWeight(TimestampedModel):
    """Scoring Weight model.

    Stores configurable contribution weights used for score calculation.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_crp_recognition_scoring_weights"
        verbose_name_plural = "Scoring Weights"

    event_type = models.CharField(
        verbose_name="Event Type",
        max_length=20,
        choices=EventTypeChoices.choices,
        unique=True,
        help_text="The type of contribution event",
    )
    score = models.PositiveIntegerField(
        verbose_name="Score",
        validators=[MinValueValidator(1)],
        help_text="Points awarded for this contribution type",
    )
    daily_cap = models.PositiveIntegerField(
        verbose_name="Daily Cap",
        null=True,
        blank=True,
        help_text="Maximum points that can be earned for this event type in a single day",
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
        help_text="Whether this scoring weight is currently active",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.get_event_type_display()} - {self.score} points"
