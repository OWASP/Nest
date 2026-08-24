"""Slack app conversation model."""

import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.slack.models.workspace import Workspace

if TYPE_CHECKING:  # pragma: no cover
    from apps.slack.models.message import Message

logger = logging.getLogger(__name__)

# How long conversations.info results can be reused on the report open path.
METADATA_MAX_AGE = timedelta(minutes=5)


class Conversation(TimestampedModel):
    """Slack Conversation model."""

    class Meta:
        """Model options."""

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
    slack_metadata_synced_at = models.DateTimeField(
        verbose_name="Slack metadata synced at",
        blank=True,
        null=True,
        help_text="When privacy and channel flags were last loaded from Slack.",
    )
    sync_messages = models.BooleanField(verbose_name="Sync messages", default=False)
    topic = models.TextField(verbose_name="Topic", blank=True, default="")
    total_members_count = models.PositiveIntegerField(verbose_name="Members count", default=0)

    # FKs.
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="channels")

    def __str__(self):
        """Channel human readable representation."""
        return f"{self.workspace} #{self.name}"

    @property
    def has_fresh_metadata(self) -> bool:
        """Return True when Slack metadata was loaded recently enough to reuse."""
        if self.slack_metadata_synced_at is None:
            return False
        return timezone.now() - self.slack_metadata_synced_at < METADATA_MAX_AGE

    @property
    def has_slack_metadata(self) -> bool:
        """Return True when privacy flags have been loaded from Slack at least once."""
        return self.slack_metadata_synced_at is not None

    @property
    def is_public_channel(self) -> bool:
        """Return True when Slack can unfurl message links for any workspace member.

        Requires a known channel classification so group chats and other
        non-channel conversations are not treated as public unfurl targets.
        """
        return (
            self.is_channel
            and not self.is_private
            and not self.is_im
            and not self.is_mpim
            and not self.is_group
        )

    @property
    def latest_message(self) -> "Message | None":
        """Get the latest message in the conversation."""
        return self.messages.order_by("-created_at").first()

    @property
    def source_label(self) -> str:
        """Return conversation label for content-report Reported From fields."""
        if self.is_im:
            return "direct message"
        if self.is_mpim:
            return "group chat"
        if self.name:
            return f"#{self.name}"
        return f"<#{self.slack_channel_id}>"

    @staticmethod
    def bulk_save(conversations, fields=None):
        """Bulk save conversations."""
        BulkSaveModel.bulk_save(Conversation, conversations, fields=fields)

    def content_origin(self, author_id: str | None = None) -> str:
        """Return Reported From text: location, optionally trailed by author."""
        if author_id:
            return f"{self.source_label} by <@{author_id}>"
        return self.source_label

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
        self.slack_metadata_synced_at = timezone.now()

        self.workspace = workspace

    @staticmethod
    def get_by_channel_id(channel_id: str, workspace: Workspace) -> "Conversation | None":
        """Return a conversation by channel id scoped to a workspace."""
        return Conversation.objects.filter(
            slack_channel_id=channel_id,
            workspace=workspace,
        ).first()

    @staticmethod
    def get_or_create(workspace: Workspace, channel_id: str) -> "Conversation":
        """Return an existing conversation or a minimal row for content reporting."""
        conversation, created = Conversation.objects.get_or_create(
            slack_channel_id=channel_id,
            defaults={
                "is_channel": channel_id.startswith("C"),
                "is_group": channel_id.startswith("G"),
                "is_im": channel_id.startswith("D"),
                "is_mpim": False,
                "name": "",
                "slack_creator_id": "",
                "sync_messages": False,
                "workspace": workspace,
            },
        )
        if not created and conversation.workspace_id != workspace.pk:
            logger.error(
                "Conversation channel_id=%s belongs to workspace=%s, expected workspace=%s",
                channel_id,
                getattr(conversation.workspace, "slack_workspace_id", conversation.workspace_id),
                workspace.slack_workspace_id,
            )
            message = f"Conversation {channel_id} belongs to a different Slack workspace"
            raise ValueError(message)
        if created:
            logger.info(
                "Created conversation for content report channel_id=%s workspace=%s",
                channel_id,
                workspace.slack_workspace_id,
            )
        return conversation

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
