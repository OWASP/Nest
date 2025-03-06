"""OWASP app conversation models."""

from django.db import models


class Conversation(models.Model):
    """Model representing a Slack conversation (channel or group)."""

    class Meta:
        db_table = "slack_conversations"
        verbose_name_plural = "Conversations"

    entity_id = models.CharField(max_length=255, unique=True)  # Slack ID of the conversation
    name = models.CharField(max_length=255)  # Channel or group name
    created_at = models.DateTimeField()  # Timestamp when the conversation was created
    is_private = models.BooleanField(default=False)  # True if the conversation is private
    is_archived = models.BooleanField(default=False)  # True if the conversation is archived
    is_general = models.BooleanField(default=False)  # True if it's the general channel
    topic = models.TextField(blank=True, default="")  # Topic of the conversation
    purpose = models.TextField(blank=True, default="")  # Purpose of the conversation
    creator_id = models.CharField(max_length=255)  # Slack user ID of the creator

    def __str__(self):
        """Return a string representation of the conversation."""
        return self.name
