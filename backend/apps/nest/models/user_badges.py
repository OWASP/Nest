"""A model representing badges linked to users (GitHub user entity)."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class UserBadge(BulkSaveModel, TimestampedModel):
    """Represents a user badge relation."""

    class Meta:
        db_table = "nest_user_badges"
        verbose_name_plural = "User badges"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "badge"],
                name="uq_userbadge_user_badge",
            ),
        ]

    note = models.CharField(
        verbose_name="Note",
        max_length=255,
        blank=True,
        default="",
        help_text="Optional note of the user badge.",
    )

    # FKs.
    badge = models.ForeignKey(
        "nest.Badge",
        related_name="users",
        on_delete=models.CASCADE,
        verbose_name="Badge",
    )
    user = models.ForeignKey(
        "github.User",
        related_name="badges",
        on_delete=models.CASCADE,
        verbose_name="User",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the user badge."""
        return f"{self.user.login} - {self.badge.name}"
