"""Nest app user model."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model for GitHub-authenticated users."""

    class Meta:
        db_table = "user"
        verbose_name_plural = "users"
        ordering = ["username"]
        indexes = [
            models.Index(fields=["username"]),
        ]

    github_id = models.CharField(
        verbose_name="GitHub ID",
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        verbose_name="Username",
        max_length=150,
        unique=True,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the user.

        Returns:
            str: The github_id or username of the user.

        """
        return self.github_id or self.username
