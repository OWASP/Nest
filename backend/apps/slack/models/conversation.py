"""OWASP app conversation models."""

from django.db import models

from apps.common.models import TimestampedModel


class Conversation(TimestampedModel):
    """Model representing a Slack conversation (channel or group)."""

    class Meta:
        db_table = "slack_conversations"
        verbose_name_plural = "Conversations"

    entity_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_general = models.BooleanField(default=False)
    topic = models.TextField(blank=True, default="")
    purpose = models.TextField(blank=True, default="")
    creator_id = models.CharField(max_length=255)

    def __str__(self):
        """Return a string representation of the conversation."""
        return self.name
