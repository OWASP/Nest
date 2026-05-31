"""Contribution score model for tracking aggregated contributor scores."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models.user import User
from apps.owasp.models.recognition_enums import TierChoices


class ContributionScore(TimestampedModel):
    """Contribution Score model.

    Stores aggregated contributor score and tier information.
    """

    class Meta:
        """Model options."""

        db_table = "recognition_contribution_scores"
        verbose_name_plural = "Contribution Scores"
        indexes = [
            models.Index(fields=["-value"], name="score_total_desc_idx"),
            models.Index(fields=["tier"], name="score_tier_idx"),
            models.Index(fields=["-nest_updated_at"], name="score_updated_desc_idx"),
        ]

    github_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="contribution_score",
        help_text="Associated GitHub user",
    )
    value = models.PositiveIntegerField(
        verbose_name="Value",
        default=0,
        help_text="Aggregated contribution score",
    )
    tier = models.CharField(
        verbose_name="Tier",
        max_length=20,
        choices=TierChoices.choices,
        default=TierChoices.BRONZE,
        help_text="Current contributor tier",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.github_user.login} - {self.tier.upper()} ({self.value} points)"
