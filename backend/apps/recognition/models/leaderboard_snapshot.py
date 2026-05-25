"""Recognition app leaderboard snapshot model."""

from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models.user import User
from apps.owasp.models.project import Project
from apps.recognition.models.enums import TierChoices


class LeaderboardSnapshot(TimestampedModel):
    """Leaderboard Snapshot model.

    Stores contributor ranking snapshots for leaderboard history and rank tracking.
    """

    class Meta:
        """Model options."""

        db_table = "recognition_leaderboard_snapshots"
        verbose_name_plural = "Leaderboard Snapshots"
        unique_together = ("github_user", "project", "snapshot_date")
        indexes = [
            models.Index(fields=["-snapshot_date"], name="leaderboard_snapshot_date_desc"),
            models.Index(fields=["global_rank"], name="leaderboard_global_rank_idx"),
            models.Index(fields=["project_rank"], name="leaderboard_project_rank_idx"),
            models.Index(fields=["tier"], name="leaderboard_tier_idx"),
            models.Index(
                fields=["snapshot_date", "-global_rank"], name="leaderboard_snapshot_rank_idx"
            ),
        ]

    github_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leaderboard_snapshots",
        help_text="Associated GitHub user",
    )
    snapshot_date = models.DateField(
        verbose_name="Snapshot Date",
        help_text="Date of the snapshot",
    )
    global_rank = models.PositiveIntegerField(
        verbose_name="Global Rank",
        validators=[MinValueValidator(1)],
        help_text="Contributor's rank across all OWASP contributions",
    )
    project_rank = models.PositiveIntegerField(
        verbose_name="Project Rank",
        validators=[MinValueValidator(1)],
        help_text="Contributor's rank within a specific project",
    )
    score = models.PositiveIntegerField(
        verbose_name="Score",
        default=0,
        help_text="Total contribution score at the time of snapshot",
    )
    tier = models.CharField(
        verbose_name="Tier",
        max_length=20,
        choices=TierChoices.choices,
        help_text="Contributor's tier at the time of snapshot",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="leaderboard_snapshots",
        help_text="The project to which this ranking applies",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return (
            f"{self.github_user.login} - Global Rank: {self.global_rank}, "
            f"Project Rank: {self.project_rank} ({self.snapshot_date})"
        )
