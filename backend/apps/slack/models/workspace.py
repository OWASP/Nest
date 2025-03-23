"""Slack app workspace model."""

from django.db import models

from apps.common.models import TimestampedModel


class Workspace(TimestampedModel):
    """Slack Workspace model."""

    class Meta:
        db_table = "slack_workspaces"
        verbose_name_plural = "Workspaces"

    slack_workspace_id = models.CharField(verbose_name="Workspace ID", max_length=50)
    name = models.CharField(verbose_name="Workspace Name", max_length=100, default="")
    bot_token = models.CharField(verbose_name="Bot Token", max_length=200, default="")

    def __str__(self):
        """Workspace human readable representation."""
        return f"{self.name or 'Unnamed'}"
