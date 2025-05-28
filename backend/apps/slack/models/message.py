"""Slack app message model."""

from datetime import UTC, datetime

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.slack.models.conversation import Conversation


class Message(TimestampedModel):
    """Slack Message model."""

    class Meta:
        db_table = "slack_messages"
        verbose_name_plural = "Messages"
        unique_together = ("conversation", "slack_message_id")

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    is_thread = models.BooleanField(verbose_name="Is Thread", default=False)
    slack_message_id = models.CharField(verbose_name="Slack Message ID", max_length=50)
    text = models.TextField(verbose_name="Message Text", blank=True)
    timestamp = models.DateTimeField(verbose_name="Message Timestamp", blank=True)

    def __str__(self):
        """Human readable representation."""
        text_display_limit = 50
        text_preview = (
            self.text[:text_display_limit] + "..."
            if len(self.text) > text_display_limit
            else self.text
        )
        return f"{text_preview}"

    @staticmethod
    def bulk_save(messages: list["Message"], fields=None) -> None:
        """Bulk save messages."""
        BulkSaveModel.bulk_save(Message, messages, fields=fields)

    @staticmethod
    def update_data(data: dict, *, save: bool = True) -> "Message":
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
            message = Message.objects.get(
                slack_message_id=slack_message_id, conversation=conversation
            )
        except Message.DoesNotExist:
            message = Message(slack_message_id=slack_message_id, conversation=conversation)

        thread_replies_list = data.get("thread_messages", [])
        if thread_replies_list:
            parent_text = data.get("text", "")
            combined_text_parts = [parent_text]
            combined_text_parts.extend(
                msg.get("text", "") for msg in thread_replies_list if msg.get("text")
            )
            message.text = "\n\n".join(filter(None, combined_text_parts))
            message.is_thread = True
        else:
            message.text = data.get("text", "")
            message.is_thread = data.get("is_thread", False)

        retrieved_timestamp = data.get("timestamp")
        if retrieved_timestamp:
            message.timestamp = datetime.fromtimestamp(float(retrieved_timestamp), tz=UTC)

        if save:
            message.save()

        return message
