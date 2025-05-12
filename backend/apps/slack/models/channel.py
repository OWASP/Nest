"""Slack app channel model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.models.workspace import Workspace


class Channel(TimestampedModel):
    """Slack Channel model."""

    class Meta:
        db_table = "slack_channels"
        verbose_name_plural = "Channels"

    is_private = models.BooleanField(verbose_name="Is Private", default=False)
    member_count = models.PositiveIntegerField(verbose_name="Member Count", default=0)
    name = models.CharField(verbose_name="Channel Name", max_length=100, default="")
    slack_channel_id = models.CharField(verbose_name="Channel ID", max_length=50, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="channels")

    def __str__(self):
        """Channel human readable representation."""
        return f"#{self.name} - {self.workspace}"

    @staticmethod
    def update_data(workspace, channel_data) -> None:
        """Update instance based on Slack data."""
        Channel.objects.update_or_create(
            slack_channel_id=channel_data["id"],
            workspace=workspace,
            defaults={
                "is_private": channel_data["is_private"],
                "member_count": channel_data.get("num_members", 0),
                "name": channel_data["name"],
            },
        )
