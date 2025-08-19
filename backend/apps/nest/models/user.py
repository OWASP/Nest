"""Nest app user model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.nest.models.api_key import ApiKey


class User(AbstractUser):
    """Nest user model."""

    class Meta:
        db_table = "nest_users"
        verbose_name_plural = "Users"
        ordering = ["username"]
        indexes = [
            models.Index(fields=["username"]),
        ]

    github_user = models.OneToOneField(
        "github.user",
        verbose_name="Github User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    # M2Ms.
    badges = models.ManyToManyField(
        "nest.Badge",
        verbose_name="Badges",
        related_name="users",
        blank=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the user.

        Returns:
            str: The user's string representation.

        """
        return self.username

    @property
    def active_api_keys(self) -> QuerySet[ApiKey]:
        """Return active API keys for the user."""
        return self.api_keys.filter(
            expires_at__gte=timezone.now(),
            is_revoked=False,
        )
