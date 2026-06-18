"""Slack app workspace model."""

import os

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.constants import OWASP_WORKSPACE_ID


# ruff: noqa: DJ001
# TODO(arkid15r): normalize NULL CharFields in restored dumps, then drop null=True.
class Workspace(TimestampedModel):
    """Slack Workspace model."""

    class Meta:
        """Model options."""

        db_table = "slack_workspaces"
        verbose_name_plural = "Workspaces"

    name = models.CharField(
        verbose_name="Workspace Name",
        max_length=100,
        default="",
    )
    slack_workspace_id = models.CharField(
        verbose_name="Workspace ID",
        max_length=50,
        unique=True,
    )
    total_members_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Members count",
    )
    invite_link_alert_channel_id = models.CharField(
        verbose_name="Invite link alert channel ID",
        max_length=32,
        blank=True,
        null=True,
        default="",
        help_text=(
            "Slack channel ID for invite-limit alerts (e.g. C..., without # prefix); "
            "empty skips posting. Used by slack_check_invite_link when posting warnings."
        ),
    )
    invite_link_alert_user_ids = models.JSONField(
        verbose_name="Invite alert Slack user IDs to mention",
        blank=True,
        null=True,
        default=None,
        help_text=(
            'Optional JSON list of Slack user IDs (e.g. ["U01ABC…"]). '
            "A trailing cc: line with <@mentions> is added to invite-limit alerts."
        ),
    )
    invite_link_alert_member_offset = models.PositiveSmallIntegerField(
        verbose_name="Member count offset for invite alert threshold",
        blank=True,
        null=True,
        default=350,
        validators=[MinValueValidator(1)],
        help_text=(
            "Added to invite_link_member_count for the alert threshold (computed, not stored). "
            "Slack shared invite cap is 400. "
            "Database may contain NULL on restored legacy rows; "
            "those use 350 in application logic."
        ),
    )
    invite_link_created_at = models.DateTimeField(
        verbose_name="Public invite link updated at",
        blank=True,
        null=True,
        help_text=(
            "Committer time of the latest matching GitHub commit for the public invite include."
        ),
    )
    invite_link_commit_sha = models.CharField(
        verbose_name="Public invite link commit SHA",
        max_length=40,
        blank=True,
        null=True,
        default="",
        help_text=(
            "Full Git SHA of the latest matching commit for _includes/slack_invite.html "
            "(used to link to the commit on GitHub)."
        ),
    )
    invite_link_member_count = models.PositiveIntegerField(
        verbose_name="Member count when invite baseline was set",
        blank=True,
        null=True,
        help_text=(
            "total_members_count from slack_sync_data when baseline was last set for the "
            "current invite link."
        ),
    )
    invite_link_last_alert_sent_at = models.DateTimeField(
        verbose_name="Last invite-limit alert sent at",
        blank=True,
        null=True,
        help_text="When slack_check_invite_link last posted an invite-limit alert to Slack.",
    )
    invite_link_last_alert_message_ts = models.CharField(
        verbose_name="Last invite-limit alert message timestamp",
        max_length=32,
        blank=True,
        null=True,
        default="",
        help_text=(
            "Slack message timestamp (ts) of the last invite-limit alert. "
            "Used to post a threaded resolution reply when the invite link is updated."
        ),
    )

    @property
    def invite_link_alert_threshold(self) -> int | None:
        """Member count at which slack_check_invite_link alerts (baseline + offset)."""
        if self.invite_link_member_count is None:
            return None
        offset = (
            self.invite_link_alert_member_offset
            if self.invite_link_alert_member_offset is not None
            else 350
        )
        return self.invite_link_member_count + offset

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
