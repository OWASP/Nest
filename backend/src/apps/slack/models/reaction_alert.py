"""Store emitted Slack reaction alerts."""

from django.core.cache import cache
from django.db import IntegrityError, models

from apps.common.models import TimestampedModel
from apps.slack.models.conversation import Conversation

LOCK_TTL_SECONDS = 30


class ReactionAlert(TimestampedModel):
    """Record that an alert was already sent for a reported message."""

    class Meta:
        """Model options."""

        db_table = "slack_reaction_alerts"
        unique_together = ("conversation", "message_ts", "report_type")

    alert_message_ts = models.CharField(
        max_length=32,
        blank=True,
        default="",
        help_text="Slack timestamp of the posted reaction alert message.",
    )
    message_ts = models.CharField(
        max_length=32,
        help_text="Slack timestamp of the message that triggered the alert.",
    )
    reaction_count = models.PositiveSmallIntegerField(default=0)
    report_type = models.CharField(
        max_length=64,
        help_text="Report category for the emitted reaction alert.",
    )
    reporter_user_ids = models.JSONField(
        blank=True,
        default=list,
        help_text="Slack user IDs that had the triggering reaction when the alert was posted.",
    )

    # FKs.
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    @staticmethod
    def acquire(conversation: Conversation, message_ts: str, report_type: str) -> bool:
        """Return True if this process should post the alert."""
        if ReactionAlert.exists_for(conversation, message_ts, report_type):
            return False

        key = ReactionAlert.lock_key(conversation, message_ts, report_type)
        if not cache.add(key, 1, timeout=LOCK_TTL_SECONDS):
            return False

        if ReactionAlert.exists_for(conversation, message_ts, report_type):
            cache.delete(key)
            return False

        return True

    @staticmethod
    def exists_for(conversation: Conversation, message_ts: str, report_type: str) -> bool:
        """Return True if an alert was already recorded for this message."""
        return ReactionAlert.objects.filter(
            conversation=conversation,
            message_ts=message_ts,
            report_type=report_type,
        ).exists()

    @staticmethod
    def lock_key(conversation: Conversation, message_ts: str, report_type: str) -> str:
        """Return the cache key for an in-flight reaction alert."""
        return f"slack:reaction-alert:{conversation.pk}:{message_ts}:{report_type}"

    @staticmethod
    def record(
        conversation: Conversation,
        message_ts: str,
        report_type: str,
        reaction_count: int,
        alert_message_ts: str,
        *,
        reporter_user_ids: list[str],
    ) -> None:
        """Store that an alert was sent, ignoring a concurrent insert."""
        try:
            ReactionAlert.objects.create(
                alert_message_ts=alert_message_ts,
                conversation=conversation,
                message_ts=message_ts,
                reaction_count=reaction_count,
                report_type=report_type,
                reporter_user_ids=reporter_user_ids,
            )
        except IntegrityError:
            return

    @staticmethod
    def release(conversation: Conversation, message_ts: str, report_type: str) -> None:
        """Release the in-flight lock so a later reaction can retry."""
        cache.delete(ReactionAlert.lock_key(conversation, message_ts, report_type))
