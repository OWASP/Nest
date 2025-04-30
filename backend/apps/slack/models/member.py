"""Slack app member model."""

from django.db import models

from apps.common.models import TimestampedModel

from .workspace import Workspace


class Member(TimestampedModel):
    """Slack Member model."""

    class Meta:
        db_table = "slack_members"
        verbose_name_plural = "Members"

    email = models.CharField(verbose_name="Email", max_length=100, default="")
    real_name = models.CharField(verbose_name="Real Name", max_length=100, default="")
    slack_user_id = models.CharField(verbose_name="User ID", max_length=50, unique=True)
    username = models.CharField(verbose_name="Username", max_length=100, default="")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="members")
    user = models.OneToOneField(
        "github.User",
        verbose_name="User",
        related_name="slack_user",
        null=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    # M2M
    suggested_users = models.ManyToManyField(
        "github.User",
        verbose_name="github_user_suggestions",
        related_name="matched_slack_users",
        blank=True,
    )

    def __str__(self):
        """Member human readable representation."""
        return f"{self.username or 'Unnamed'} ({self.slack_user_id})"
