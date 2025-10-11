"""Slack app member model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel

from .workspace import Workspace


class Member(TimestampedModel):
    """Slack Member model."""

    class Meta:
        db_table = "slack_members"
        verbose_name_plural = "Members"

    email = models.CharField(verbose_name="Email", max_length=100, default="")
    is_bot = models.BooleanField(verbose_name="Is bot", default=False)
    real_name = models.CharField(verbose_name="Real Name", max_length=100, default="")
    slack_user_id = models.CharField(verbose_name="User ID", max_length=50, unique=True)
    username = models.CharField(verbose_name="Username", max_length=100, default="")

    # FKs.
    user = models.ForeignKey(
        "github.User",
        verbose_name="User",
        related_name="slack_users",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="members",
    )

    # M2Ms.
    suggested_users = models.ManyToManyField(
        "github.User",
        verbose_name="Github user suggestions",
        related_name="suggested_slack_users",
        blank=True,
    )

    def __str__(self):
        """Member human readable representation."""
        return f"{self.username or 'Unnamed'} ({self.slack_user_id})"

    def from_slack(self, member_data, workspace: Workspace) -> None:
        """Update instance based on Slack member data."""
        self.email = member_data.get("profile", {}).get("email", "")
        self.is_bot = member_data["is_bot"]
        self.real_name = member_data.get("real_name", "")
        self.slack_user_id = member_data["id"]
        self.username = member_data["name"]

        self.workspace = workspace

    @staticmethod
    def bulk_save(members, fields=None):
        """Bulk save members."""
        BulkSaveModel.bulk_save(Member, members, fields=fields)

    @staticmethod
    def update_data(member_data, workspace, *, save=True) -> None:
        """Update instance based on Slack data."""
        member_id = member_data["id"]
        try:
            member = Member.objects.get(slack_user_id=member_id)
        except Member.DoesNotExist:
            member = Member(slack_user_id=member_id)

        member.from_slack(member_data, workspace)
        if save:
            member.save()

        return member
