"""A model representing badges linked to users (GitHub user entity)."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class UserBadge(BulkSaveModel, TimestampedModel):
    """Represents a user badge relation."""

    class Meta:
        db_table = "nest_user_badges"
        unique_together = (
            "badge",
            "user",
        )
        verbose_name_plural = "User badges"

    is_active = models.BooleanField(
        default=True,
        verbose_name="Is active",
        help_text="Indicates if the badge assignment is active.",
    )
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
        related_name="user_badges",
        on_delete=models.CASCADE,
        verbose_name="User",
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the user badge."""
        return f"{self.user.login} - {self.badge.name}"

    @staticmethod
    def bulk_save(user_badges, fields=None) -> None:  # type: ignore[override]
        """Bulk save user badges."""
        BulkSaveModel.bulk_save(UserBadge, user_badges, fields=fields)
