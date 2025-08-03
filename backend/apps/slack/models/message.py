"""Slack app message model."""

import re
from datetime import UTC, datetime

import emoji
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

    created_at = models.DateTimeField(verbose_name="Created at")
    has_replies = models.BooleanField(verbose_name="Has replies", default=False)
    raw_data = models.JSONField(verbose_name="Raw data", default=dict)
    slack_message_id = models.CharField(verbose_name="Slack message ID", max_length=50)

    # FKs.
    author = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="messages", blank=True, null=True
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="thread_replies",
        null=True,
        blank=True,
    )

    def __str__(self):
        """Human readable representation."""
        return (
            f"{self.raw_data['channel']} huddle"
            if self.raw_data.get("subtype") == "huddle_thread"
            else truncate(self.raw_data["text"], 50)
        )

    @property
    def cleaned_text(self) -> str:
        """Get cleaned text from the message."""
        if not self.text:
            return ""

        text = emoji.demojize(self.text)  # Remove emojis.
        text = re.sub(r"<@U[A-Z0-9]+>", "", text)  # Remove user mentions.
        text = re.sub(r"<https?://[^>]+>", "", text)  # Remove links.
        text = re.sub(r":\w+:", "", text)  # Remove emoji aliases.
        text = re.sub(r"\s+", " ", text)  # Normalize whitespace.

        return text.strip()

    @property
    def latest_reply(self) -> "Message | None":
        """Get the latest reply to this message."""
        return (
            Message.objects.filter(
                conversation=self.conversation,
                parent_message=self,
            )
            .order_by("-created_at")
            .first()
        )

    @property
    def subtype(self) -> str | None:
        """Get the subtype of the message if it exists."""
        return self.raw_data.get("subtype")

    @property
    def text(self) -> str:
        """Get the text of the message."""
        return self.raw_data.get("text", "")

    @property
    def ts(self) -> str:
        """Get the message timestamp."""
        return self.raw_data["ts"]

    @property
    def url(self):
        """Return message URL."""
        return (
            f"https://{self.conversation.workspace.name.lower()}.slack.com/archives/"
            f"{self.conversation.slack_channel_id}/"
            f"p{self.slack_message_id.replace('.', '')}"
        )

    def from_slack(
        self,
        message_data: dict,
        conversation: Conversation,
        author: "Member | None" = None,
        *,
        parent_message: "Message | None" = None,
    ) -> None:
        """Update instance based on Slack message data."""
        self.created_at = datetime.fromtimestamp(float(message_data["ts"]), tz=UTC)
        self.has_replies = message_data.get("reply_count", 0) > 0
        self.is_bot = message_data.get("bot_id") is not None
        self.raw_data = message_data
        self.slack_message_id = message_data.get("ts", "")

        self.author = author
        self.conversation = conversation
        self.parent_message = parent_message

    @staticmethod
    def bulk_save(messages: list["Message"], fields=None) -> None:
        """Bulk save messages."""
        BulkSaveModel.bulk_save(Message, messages, fields=fields)

    @staticmethod
    def update_data(
        data: dict,
        conversation: Conversation,
        author: Member | None = None,
        *,
        parent_message: "Message | None" = None,
        save: bool = True,
    ) -> "Message":
        """Update message data.

        Args:
          data (dict): Data to update the message with.
          conversation (Conversation): The conversation the message belongs to.
          author (Member): The author of the message.
          parent_message (Message | None): The parent message if this is a thread reply.
          save (bool): Whether to save the message to the database.

        Returns:
          Message: The updated message instance.

        """
        slack_message_id = data["ts"]
        try:
            message = Message.objects.get(
                slack_message_id=slack_message_id, conversation=conversation
            )
        except Message.DoesNotExist:
            message = Message(slack_message_id=slack_message_id, conversation=conversation)

        message.from_slack(data, conversation, author, parent_message=parent_message)

        if save:
            message.save()

        return message
