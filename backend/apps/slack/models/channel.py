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

    def from_slack(self, conversation_data):
        """Update instance based on Slack conversation data."""
        created_timestamp = int(conversation_data.get("created", 0))
        created_datetime = datetime.fromtimestamp(created_timestamp, tz=timezone.utc)
        self.name = conversation_data.get("name", "")
        self.created_at = created_datetime
        self.is_private = conversation_data.get("is_private", False)
        self.is_archived = conversation_data.get("is_archived", False)
        self.is_general = conversation_data.get("is_general", False)
        self.topic = conversation_data.get("topic", {}).get("value", "")
        self.purpose = conversation_data.get("purpose", {}).get("value", "")
        self.creator_id = conversation_data.get("creator", "")

    @staticmethod
    def bulk_save(conversations, fields=None):
        """Bulk save conversations."""
        BulkSaveModel.bulk_save(Conversation, conversations, fields=fields)

    @staticmethod
    def update_data(conversation_data, save=True):
        """Update Conversation data from Slack.

        Args:
            conversation_data: Dictionary with conversation data from Slack API
            save: Whether to save the model after updating

        Returns:
            Updated or created Conversation instance, or None if error

        """
        channel_id = conversation_data["id"]
        try:
            conversation = Conversation.objects.get(entity_id=channel_id)
        except Conversation.DoesNotExist:
            conversation = Conversation(entity_id=channel_id)

        conversation.from_slack(conversation_data)

        if save:
            conversation.save()

        return conversation
