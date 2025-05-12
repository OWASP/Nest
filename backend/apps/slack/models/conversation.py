"""Slack app conversation model."""

import logging
from datetime import UTC, datetime

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel

logger = logging.getLogger(__name__)


class Conversation(BulkSaveModel, TimestampedModel):
    """conversation model."""

    class Meta:
        db_table = "slack_conversations"
        verbose_name_plural = "Conversations"

    created_at = models.DateTimeField(verbose_name="Created At", blank=True, null=True)
    creator_id = models.CharField(verbose_name="Creator ID", max_length=255)
    entity_id = models.CharField(verbose_name="Entity ID", max_length=255, unique=True)
    is_archived = models.BooleanField(verbose_name="Is Archived", default=False)
    is_general = models.BooleanField(verbose_name="Is General", default=False)
    is_private = models.BooleanField(verbose_name="Is Private", default=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    purpose = models.TextField(verbose_name="Purpose", blank=True, default="")
    topic = models.TextField(verbose_name="Topic", blank=True, default="")

    def __str__(self):
        """Return a string representation of the conversation."""
        return self.name

    def from_slack(self, conversation_data):
        """Update instance based on Slack conversation data."""
        created_timestamp = int(conversation_data.get("created", 0))
        created_datetime = datetime.fromtimestamp(created_timestamp, tz=UTC)
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
