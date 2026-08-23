"""Slack app message model."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, unquote, urlparse

import emoji
from django.db import models
from slack_sdk.errors import SlackApiError, SlackClientError

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate
from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member

if TYPE_CHECKING:
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)

ARCHIVE_PATH_RE = re.compile(
    r"^/archives/(?P<channel>[CGD][A-Z0-9]+)/p(?P<compact_ts>\d+)$",
    re.IGNORECASE,
)
COMPACT_TS_FRACTION_DIGITS = 6
VISIBILITY_ERRORS = frozenset(
    {
        "channel_not_found",
        "is_archived",
        "missing_scope",
        "not_in_channel",
    }
)


class Message(TimestampedModel):
    """Slack Message model."""

    class Meta:
        """Model options."""

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
    def latest_reply(self) -> Message | None:
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
        author: Member | None = None,
        *,
        parent_message: Message | None = None,
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
    def bulk_save(messages: list[Message], fields=None) -> None:
        """Bulk save messages."""
        BulkSaveModel.bulk_save(Message, messages, fields=fields)

    @staticmethod
    def compact_ts_to_message_ts(compact_ts: str) -> str:
        """Convert a Slack permalink p-timestamp to a message ts."""
        if len(compact_ts) <= COMPACT_TS_FRACTION_DIGITS:
            return ""
        return (
            f"{compact_ts[:-COMPACT_TS_FRACTION_DIGITS]}"
            f".{compact_ts[-COMPACT_TS_FRACTION_DIGITS:]}"
        )

    @staticmethod
    def fetch_permalink(client: WebClient, channel_id: str, message_ts: str) -> str:
        """Return a Slack permalink for the message, or an empty string."""
        try:
            return (
                client.chat_getPermalink(
                    channel=channel_id,
                    message_ts=message_ts,
                ).get("permalink")
                or ""
            )
        except SlackApiError as e:
            logger.warning(
                "Could not fetch Slack permalink: %s",
                e.response.get("error", "unknown_error"),
            )
            return ""
        except SlackClientError as e:
            logger.warning("Could not fetch Slack permalink: %s", e)
            return ""

    @staticmethod
    def fetch_payload(
        client: WebClient,
        channel_id: str,
        message_ts: str,
        thread_ts: str | None = None,
    ) -> dict[str, Any] | None:
        """Fetch a Slack message payload, or None when missing / not visible."""
        try:
            found: dict[str, Any] | None = None

            if thread_ts and thread_ts != message_ts:
                response = client.conversations_replies(
                    channel=channel_id,
                    ts=thread_ts,
                    latest=message_ts,
                    oldest=message_ts,
                    inclusive=True,
                    limit=1,
                )
                found = Message.find_in_api_list(response.get("messages") or [], message_ts)

            if found is None:
                response = client.conversations_history(
                    channel=channel_id,
                    latest=message_ts,
                    oldest=message_ts,
                    inclusive=True,
                    limit=1,
                )
                found = Message.find_in_api_list(response.get("messages") or [], message_ts)
        except SlackApiError as e:
            error = e.response.get("error", "unknown_error")
            if error in VISIBILITY_ERRORS:
                logger.info(
                    "NestBot cannot fetch message channel_id=%s ts=%s error=%s",
                    channel_id,
                    message_ts,
                    error,
                )
            else:
                logger.warning(
                    "Failed to fetch message channel_id=%s ts=%s error=%s",
                    channel_id,
                    message_ts,
                    error,
                )
            return None
        except SlackClientError as e:
            logger.warning(
                "Failed to fetch message channel_id=%s ts=%s error=%s",
                channel_id,
                message_ts,
                e,
            )
            return None
        else:
            return found

    @staticmethod
    def find_in_api_list(
        messages: list[dict[str, Any]],
        message_ts: str,
    ) -> dict[str, Any] | None:
        """Return the message matching message_ts from a Slack messages list."""
        for item in messages:
            if item.get("ts") == message_ts:
                return item
        return None

    @staticmethod
    def get_author_id(message_payload: dict[str, Any]) -> str | None:
        """Return the Slack user id of the message author when present."""
        return user if isinstance(user := message_payload.get("user"), str) and user else None

    @staticmethod
    def get_raw_data_by_channel_and_ts(channel_id: str, message_ts: str) -> dict | None:
        """Return stored Slack raw_data for a channel message, if present."""
        existing = (
            Message.objects.filter(
                conversation__slack_channel_id=channel_id,
                slack_message_id=message_ts,
            )
            .only("raw_data")
            .first()
        )
        if existing is not None and isinstance(existing.raw_data, dict) and existing.raw_data:
            return existing.raw_data
        return None

    @staticmethod
    def load_payload(
        client: WebClient,
        channel_id: str,
        message_ts: str,
        thread_ts: str | None = None,
    ) -> dict[str, Any] | None:
        """Return a message payload from Nest DB or Slack API."""
        if raw_data := Message.get_raw_data_by_channel_and_ts(channel_id, message_ts):
            return raw_data
        return Message.fetch_payload(client, channel_id, message_ts, thread_ts)

    @staticmethod
    def parse_permalink(raw: str) -> tuple[str, str, str | None] | None:
        """Parse channel_id, message_ts, and optional thread_ts from a Slack archive URL."""
        url = Message.unwrap_slack_link(raw)
        if not url:
            return None

        parsed = urlparse(url if "://" in url else f"https://{url}")
        match = ARCHIVE_PATH_RE.match(parsed.path or "")
        if match is None:
            return None

        message_ts = Message.compact_ts_to_message_ts(match.group("compact_ts"))
        if not message_ts:
            return None

        query = parse_qs(parsed.query or "")
        thread_values = query.get("thread_ts") or []
        thread_ts = thread_values[0] if thread_values else None
        if thread_ts is not None and not re.fullmatch(r"\d+\.\d+", thread_ts):
            thread_ts = None

        return match.group("channel"), message_ts, thread_ts

    @staticmethod
    def unwrap_slack_link(raw: str) -> str:
        """Strip Slack link markup and return the URL, ignoring trailing text."""
        text = (raw or "").strip()
        if text.startswith("<"):
            end = text.find(">")
            if end != -1:
                text = text[1:end]
                if "|" in text:
                    text = text.split("|", 1)[0]
                return unquote(text.strip())
        token = text.split(None, 1)[0] if text else ""
        return unquote(token)

    @staticmethod
    def update_data(
        data: dict,
        conversation: Conversation,
        author: Member | None = None,
        *,
        parent_message: Message | None = None,
        save: bool = True,
    ) -> Message:
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
