"""Badge model for OWASP Nest user achievements and roles."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class Badge(BulkSaveModel, TimestampedModel):
    """Represents a user badge for roles or achievements."""

    class Meta:
        db_table = "nest_badges"
        ordering = ["weight", "name"]
        verbose_name_plural = "Badges"

    css_class = models.CharField(
        verbose_name="CSS Class",
        max_length=255,
        default="",
    )
    description = models.CharField(
        verbose_name="Description",
        max_length=255,
        blank=True,
        default="",
    )
    name = models.CharField(
        verbose_name="Name",
        max_length=255,
        unique=True,
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name="Weight",
        default=0,
    )


class UserBadge(TimestampedModel):
    """Through model for User and Badge."""

    class Meta:
        db_table = "nest_user_badges"
        verbose_name_plural = "User badges"
        unique_together = ("user", "badge")

    user = models.ForeignKey("nest.User", on_delete=models.CASCADE)
    badge = models.ForeignKey("nest.Badge", on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return a human-readable representation of the user badge."""
        return f"{self.user} - {self.badge}"


class GithubUserBadge(TimestampedModel):
    """Through model for Github User and Badge."""

    class Meta:
        db_table = "nest_github_user_badges"
        verbose_name_plural = "GitHub user badges"
        unique_together = ("github_user", "badge")

    github_user = models.ForeignKey("github.User", on_delete=models.CASCADE)
    badge = models.ForeignKey("nest.Badge", on_delete=models.CASCADE)
    def __str__(self) -> str:
        """Return the badge string representation."""
        return f"{self.github_user} - {self.badge}"
