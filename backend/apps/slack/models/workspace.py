"""Slack app workspace model."""

import os

from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.constants import OWASP_WORKSPACE_ID


class Workspace(TimestampedModel):
    """Slack Workspace model."""

    class Meta:
        """Model options."""

        db_table = "slack_workspaces"
        verbose_name_plural = "Workspaces"

    name = models.CharField(verbose_name="Workspace Name", max_length=100, default="")
    slack_workspace_id = models.CharField(verbose_name="Workspace ID", max_length=50, unique=True)
    total_members_count = models.PositiveIntegerField(default=0, verbose_name="Members count")

    def __str__(self):
        """Workspace human readable representation."""
        return f"{self.name or self.slack_workspace_id}"

    @staticmethod
    def get_default_workspace() -> "Workspace | None":
        """Get the default workspace.

        Returns:
            Workspace: The default workspace or None.

        """
        return Workspace.objects.filter(slack_workspace_id=OWASP_WORKSPACE_ID).first()

    @property
    def bot_token(self) -> str:
        """Get bot token for the workspace.

        Returns:
            str: The bot token for the workspace.

        """
        return os.getenv(f"SLACK_BOT_TOKEN_{self.slack_workspace_id.upper()}", "")
