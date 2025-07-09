"""Nest app user model."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model for GitHub-authenticated users."""

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

    def __str__(self) -> str:
        """Return a human-readable representation of the user.

        Returns:
            str: The user's string representation.

        """
        return self.username
