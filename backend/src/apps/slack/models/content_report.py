"""Store emitted Slack content reports (emoji and shortcut)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import uuid4

from django.core.cache import cache
from django.db import IntegrityError, models, transaction
from slack_sdk.errors import SlackApiError, SlackClientError

from apps.common.models import TimestampedModel
from apps.slack.blocks import markdown
from apps.slack.common.text import preview_text
from apps.slack.enums import ReportSource, ReportType
from apps.slack.models.conversation import Conversation
from apps.slack.models.message import Message
from apps.slack.utils.reaction import mention_users

if TYPE_CHECKING:
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)

LOCK_TTL_SECONDS = 120


class ContentReport(TimestampedModel):
    """Record that a content report alert was already sent for a message."""

    class Meta:
        """Model options."""

        db_table = "slack_content_reports"
        constraints = [
            models.UniqueConstraint(
                fields=("conversation", "message_ts"),
                name="unique_contentreport_conversation_message_ts",
                violation_error_message=(
                    "A content report already exists for this conversation and message."
                ),
            ),
        ]

    alert_message_ts = models.CharField(
        max_length=32,
        blank=True,
        default="",
        help_text="Slack timestamp of the posted moderation alert message.",
    )
    message_ts = models.CharField(
        max_length=32,
        help_text="Slack timestamp of the reported message.",
    )
    reaction_count = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Unique emoji reporters at alert time; null for shortcut/command reports.",
    )
    report_type = models.CharField(
        max_length=64,
        choices=ReportType.choices,
        default=ReportType.SPAM,
        help_text="Report category for the emitted content report.",
    )
    reporter_user_ids = models.JSONField(
        blank=True,
        default=list,
        help_text="Slack user IDs that triggered this content report.",
    )
    source = models.CharField(
        max_length=32,
        choices=ReportSource.choices,
        help_text="Whether this report came from emoji, a message shortcut, or /report.",
    )

    # FKs.
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="content_reports",
        help_text="Stored Slack message when available (required for shortcut/command reports).",
    )

    @staticmethod
    def acquire(conversation: Conversation, message_ts: str) -> str | None:
        """Return a lock owner if this process should post the alert."""
        if ContentReport.exists_for(conversation, message_ts):
            return None

        key = ContentReport.lock_key(conversation, message_ts)
        owner = uuid4().hex
        if not cache.add(key, owner, timeout=LOCK_TTL_SECONDS):
            return None

        if ContentReport.exists_for(conversation, message_ts):
            ContentReport.release(conversation, message_ts, owner)
            return None

        return owner

    @staticmethod
    def build_alert_text(
        *,
        workspace,
        conversation: Conversation,
        message: Message,
        reporter_user_id: str,
        report_type: str,
        permalink: str = "",
    ) -> str:
        """Build the moderation-channel alert text for a content report."""
        alert_users = mention_users(workspace.content_report_alert_user_ids or [])
        author_id = message.raw_data.get("user") if isinstance(message.raw_data, dict) else None
        where = conversation.content_origin
        category = (
            ReportType(report_type).label if report_type in ReportType.values else report_type
        )
        lines = [
            alert_users,
            f"Content report ({category.lower()}) from <@{reporter_user_id}> in {where}.",
        ]
        if author_id:
            lines.append(f"Author: <@{author_id}>")
        quoted = preview_text(message.text)
        if quoted:
            lines.append(f">{quoted}")
        if permalink:
            lines.append(permalink)
        return "\n".join(line for line in lines if line).strip()

    @staticmethod
    def deliver_alert(
        client: WebClient,
        *,
        channel_id: str,
        text: str,
        conversation: Conversation,
        message_ts: str,
        report_type: str,
        source: ReportSource | str,
        reporter_user_ids: list[str],
        reaction_count: int | None = None,
        message: Message | None = None,
    ) -> bool:
        """Post an alert to Slack and record the content report. Return True on success."""
        try:
            alert = client.chat_postMessage(
                blocks=[markdown(text)],
                channel=channel_id,
                text=text,
            )
        except SlackApiError as e:
            logger.warning(
                "Could not post content report alert: %s",
                e.response.get("error", "unknown_error"),
            )
            return False
        except SlackClientError as e:
            logger.warning("Could not post content report alert: %s", e)
            return False

        ContentReport.record(
            conversation,
            message_ts,
            report_type,
            alert.get("ts", ""),
            source=str(source),
            reporter_user_ids=reporter_user_ids,
            reaction_count=reaction_count,
            message=message,
        )
        return True

    @staticmethod
    def exists_for(conversation: Conversation, message_ts: str) -> bool:
        """Return True if a content report was already recorded for this message."""
        return ContentReport.objects.filter(
            conversation=conversation,
            message_ts=message_ts,
        ).exists()

    @staticmethod
    def is_self_report(reporter_user_id: str, author_id: str | None) -> bool:
        """Return True when the reporter is the message author."""
        return bool(author_id) and reporter_user_id == author_id

    @staticmethod
    def lock_key(conversation: Conversation, message_ts: str) -> str:
        """Return the cache key for an in-flight content report."""
        return f"slack:content-report:{conversation.pk}:{message_ts}"

    @staticmethod
    def record(
        conversation: Conversation,
        message_ts: str,
        report_type: str,
        alert_message_ts: str,
        *,
        source: ReportSource | str,
        reporter_user_ids: list[str],
        reaction_count: int | None = None,
        message: Message | None = None,
    ) -> None:
        """Store that an alert was sent, ignoring a concurrent unique insert."""
        try:
            with transaction.atomic():
                ContentReport.objects.create(
                    alert_message_ts=alert_message_ts,
                    conversation=conversation,
                    message=message,
                    message_ts=message_ts,
                    reaction_count=reaction_count,
                    report_type=report_type,
                    reporter_user_ids=reporter_user_ids,
                    source=str(source),
                )
        except IntegrityError:
            if ContentReport.exists_for(conversation, message_ts):
                return
            raise

    @staticmethod
    def release(conversation: Conversation, message_ts: str, owner: str) -> None:
        """Release the in-flight lock if this process still owns it."""
        key = ContentReport.lock_key(conversation, message_ts)
        if cache.get(key) == owner:
            cache.delete(key)

    @staticmethod
    def renew(conversation: Conversation, message_ts: str, owner: str) -> bool:
        """Extend the lock TTL if this process still owns it."""
        key = ContentReport.lock_key(conversation, message_ts)
        if cache.get(key) != owner:
            return False
        return bool(cache.touch(key, LOCK_TTL_SECONDS))
