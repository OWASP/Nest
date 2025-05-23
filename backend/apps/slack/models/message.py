"""Slack app message model."""

from datetime import datetime, timezone
from typing import List
from django.db import models
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.slack.models.conversation import Conversation

class Message(TimestampedModel):
  """Slack Message model."""
  
  class Meta:
    db_table = "slack_messages"
    verbose_name_plural = "Messages"
    unique_together = ("conversation", "slack_message_id")

  conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
  reply_count = models.PositiveIntegerField(verbose_name="Reply Count", default=0)
  slack_message_id = models.CharField(verbose_name="Slack Message ID", max_length=50)
  text = models.TextField(verbose_name="Message Text", blank=True)
  thread_timestamp = models.CharField(verbose_name="Thread Timestamp", blank=True, null=True)
  timestamp = models.DateTimeField(verbose_name="Message Timestamp",blank=True, null=True)

  def __str__(self):
    """Human readable representation."""
    text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
    return f"{text_preview}"

  @property
  def is_thread_parent(self) -> bool:
    """Check if this message is a thread parent."""
    return self.reply_count > 0

  @property
  def is_thread_reply(self) -> bool:
    """Check if this message is a thread reply."""
    return bool(self.thread_timestamp and self.thread_timestamp != self.slack_message_id)

  def get_thread_messages(self):
    """Get all messages in the same thread."""
    if not self.thread_timestamp:
      return Message.objects.none()
    
    return Message.objects.filter(
      conversation=self.conversation,
      thread_timestamp=self.thread_timestamp
    ).order_by('timestamp')

  @staticmethod
  def bulk_save(messages: List['Message'], fields=None) -> None:
    """Bulk save messages."""
    BulkSaveModel.bulk_save(Message, messages, fields=fields)

  @staticmethod
  def update_data(data: dict, *, save: bool = True) -> 'Message':
    """Update message data.
    
    Args:
      data (dict): Data to update the message with.
      save (bool): Whether to save the message to the database.

    Returns:
      Message: The updated message instance.

    """
    slack_message_id = data.get("slack_message_id")
    conversation = data.get("conversation")

    try:
      message = Message.objects.get(slack_message_id=slack_message_id, conversation=conversation)
    except Message.DoesNotExist:
      message = Message(slack_message_id=slack_message_id, conversation=conversation)

    message.text = data.get("text", "")
    message.reply_count = data.get("reply_count", 0)
    message.thread_timestamp = data.get("thread_timestamp")
    retrieved_timestamp = data.get("timestamp")
    if retrieved_timestamp:
      message.timestamp = datetime.fromtimestamp(float(retrieved_timestamp), tz=timezone.utc)

    if save:
      message.save()

    return message