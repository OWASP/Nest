"""Slack app message model."""

from datetime import UTC, datetime

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate
from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member


class Message(TimestampedModel):
    """Slack Message model."""

    class Meta:
        db_table = "slack_messages"
        verbose_name_plural = "Messages"
        unique_together = ("conversation", "slack_message_id")

    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="messages")
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    is_thread_parent = models.BooleanField(verbose_name="Is Thread", default=False)
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="thread_replies",
        null=True,
        blank=True,
    )
    slack_message_id = models.CharField(verbose_name="Slack Message ID", max_length=50)
    text = models.TextField(verbose_name="Message Text", blank=True)
    created_at = models.DateTimeField(verbose_name="Created at", blank=True)

    def __str__(self):
        """Human readable representation."""
        return truncate(self.text, 50)

    def from_slack(
        self,
        message_data: dict,
        conversation: Conversation,
        author: Member,
        *,
        is_thread_reply: bool = False,
        parent_message: "Message | None" = None,
    ) -> None:
        """Update instance based on Slack message data."""
        self.slack_message_id = message_data.get("ts", "")
        self.conversation = conversation
        self.text = message_data.get("text", "")
        self.author = author

        self.is_thread_parent = not is_thread_reply and message_data.get("reply_count", 0) > 0

        if is_thread_reply and parent_message:
            self.parent_message = parent_message

        if ts := message_data.get("ts"):
            self.timestamp = datetime.fromtimestamp(float(ts), tz=UTC)

    @staticmethod
    def bulk_save(messages: list["Message"], fields=None) -> None:
        """Bulk save messages."""
        BulkSaveModel.bulk_save(Message, messages, fields=fields)

    @staticmethod
    def update_data(
        data: dict,
        conversation: Conversation,
        author: Member,
        *,
        save: bool = True,
        is_thread_reply: bool = False,
        parent_message: "Message | None" = None,
    ) -> "Message":
        """Update message data.

        Args:
          data (dict): Data to update the message with.
          save (bool): Whether to save the message to the database.
          conversation (Conversation): The conversation the message belongs to.
          author (Member): The author of the message.
          is_thread_reply (bool): Whether the message is a reply in a thread.
          parent_message (Message | None): The parent message if this is a thread reply.

        Returns:
          Message: The updated message instance.

        """
        slack_message_id = data.get("ts")
        try:
            message = Message.objects.get(
                slack_message_id=slack_message_id, conversation=conversation
            )
        except Message.DoesNotExist:
            message = Message(slack_message_id=slack_message_id, conversation=conversation)

        message.from_slack(
            data,
            conversation=conversation,
            author=author,
            is_thread_reply=is_thread_reply,
            parent_message=parent_message,
        )

        if save:
            message.save()

        return message
