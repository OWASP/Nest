"""OWASP app snapshot subscription model."""

import uuid

from django.db import models

from apps.nest.models import User


class SnapshotSubscription(models.Model):
    """Model representing a user's subscription to snapshot digest emails."""

    class Meta:
        """Model options."""

        db_table = "owasp_snapshot_subscriptions"
        verbose_name_plural = "Snapshot Subscriptions"
        indexes = [
            models.Index(fields=["is_active"], name="owasp_sub_active_idx"),
        ]

    class Frequency(models.TextChoices):
        """Subscription frequency choices."""

        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    class Status(models.TextChoices):
        """Subscription status choices."""

        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="snapshot_subscription",
    )
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    # Content preferences
    include_chapters = models.BooleanField(default=True)
    include_events = models.BooleanField(default=True)
    include_issues = models.BooleanField(default=True)
    include_posts = models.BooleanField(default=True)
    include_projects = models.BooleanField(default=True)
    include_pull_requests = models.BooleanField(default=True)
    include_releases = models.BooleanField(default=True)
    include_users = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        status = "active" if self.is_active else "inactive"
        return f"{self.user} ({self.frequency}, {status})"

    @property
    def content_preferences(self):
        """Return a dictionary of content preference settings."""
        return {
            "chapters": self.include_chapters,
            "events": self.include_events,
            "issues": self.include_issues,
            "posts": self.include_posts,
            "projects": self.include_projects,
            "pull_requests": self.include_pull_requests,
            "releases": self.include_releases,
            "users": self.include_users,
        }
