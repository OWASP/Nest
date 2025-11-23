"""Slack app conversation model."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.slack.models.workspace import Workspace

if TYPE_CHECKING:  # pragma: no cover
    from apps.slack.models.message import Message


class Conversation(TimestampedModel):
    """Slack Conversation model."""

    class Meta:
        db_table = "slack_conversations"
        verbose_name_plural = "Conversations"

    # Slack conversation attributes.
    created_at = models.DateTimeField(verbose_name="Created at", blank=True, null=True)
    is_archived = models.BooleanField(verbose_name="Is archived", default=False)
    is_channel = models.BooleanField(verbose_name="Is channel", default=False)
    is_general = models.BooleanField(verbose_name="Is general", default=False)
    is_group = models.BooleanField(verbose_name="Is group", default=False)
    is_im = models.BooleanField(verbose_name="Is IM", default=False)
    is_mpim = models.BooleanField(verbose_name="Is MPIM", default=False)
    is_nest_bot_assistant_enabled = models.BooleanField(
        verbose_name="Is Nest Bot Assistant Enabled", default=False
    )
    is_private = models.BooleanField(verbose_name="Is private", default=False)
    is_shared = models.BooleanField(verbose_name="Is shared", default=False)
    name = models.CharField(verbose_name="Name", max_length=100, default="")
    purpose = models.TextField(verbose_name="Purpose", blank=True, default="")
    slack_channel_id = models.CharField(verbose_name="Channel ID", max_length=50, unique=True)
    slack_creator_id = models.CharField(verbose_name="Creator ID", max_length=255)
    topic = models.TextField(verbose_name="Topic", blank=True, default="")
    total_members_count = models.PositiveIntegerField(verbose_name="Members count", default=0)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="channels")

    # Additional attributes.
    sync_messages = models.BooleanField(verbose_name="Sync messages", default=False)

    def __str__(self):
        """Channel human readable representation."""
        return f"{self.workspace} #{self.name}"

    @property
    def latest_message(self) -> "Message | None":
        """Get the latest message in the conversation."""
        return self.messages.order_by("-created_at").first()

    def from_slack(self, conversation_data, workspace: Workspace) -> None:
        """Update instance based on Slack conversation data."""
        self.created_at = datetime.fromtimestamp(int(conversation_data.get("created", 0)), tz=UTC)

        for attr_name in (
            "is_archived",
            "is_channel",
            "is_general",
            "is_group",
            "is_im",
            "is_mpim",
            "is_private",
            "is_shared",
        ):
            setattr(self, attr_name, conversation_data.get(attr_name, False))

        self.name = conversation_data.get("name", "")
        self.purpose = conversation_data.get("purpose", {}).get("value", "")
        self.slack_creator_id = conversation_data.get("creator", "")
        self.topic = conversation_data.get("topic", {}).get("value", "")
        self.total_members_count = conversation_data.get("num_members", 0)

        self.workspace = workspace

    @staticmethod
    def bulk_save(conversations, fields=None):
        """Bulk save conversations."""
        BulkSaveModel.bulk_save(Conversation, conversations, fields=fields)

    @staticmethod
    def update_data(conversation_data, workspace, *, save=True):
        """Update Channel data from Slack.

        Args:
            workspace (Workspace): Workspace instance
            conversation_data: Dictionary with conversation data from Slack API
            save: Whether to save the model after updating

        Returns:
            Updated or created Channel instance, or None if error

        """
        channel_id = conversation_data["id"]
        try:
            conversation = Conversation.objects.get(slack_channel_id=channel_id)
        except Conversation.DoesNotExist:
            conversation = Conversation(slack_channel_id=channel_id)

        conversation.from_slack(conversation_data, workspace)
        if save:
            conversation.save()

        return conversation
