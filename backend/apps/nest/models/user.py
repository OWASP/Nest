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

    github_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="GitHub ID",
    )

    github_user = models.OneToOneField(
        "github.user",
        verbose_name="Github User",
        null=True,
        blank=False,
        unique=True,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the user.

        Returns:
            str: The github_id or username of the user.

        """
        return self.username
