"""Notification utils."""

import json
import logging

from django.core.mail import send_mail
from django.utils.timezone import now
from django_redis import get_redis_connection

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.event import Event
from apps.owasp.models.notification import Notification
from apps.owasp.models.snapshot import Snapshot

logger = logging.getLogger(__name__)

STREAM_KEY = "owasp_notifications"


def publish_snapshot_notification(snapshot: Snapshot) -> None:
    """Publish a notification for a published snapshot."""
    try:
        redis_conn = get_redis_connection("default")
        message = {
            "type": "snapshot_published",
            "snapshot_id": str(snapshot.id),
            "timestamp": str(now().timestamp()),
        }
        redis_conn.xadd(STREAM_KEY, message)
        logger.info("Published snapshot notification for snapshot %s", snapshot.id)
    except Exception:
        logger.exception(
            "Failed to publish snapshot notification for snapshot %s",
            snapshot.id,
        )


def publish_chapter_notification(
    chapter: Chapter, trigger: str, changed_fields: dict | None = None
) -> None:
    """Publish a notification for a chapter creation or update.

    Args:
        chapter: The Chapter instance.
        trigger: Either "created" or "updated".
        changed_fields: Dict of changed fields with old/new values (only for updates).

    """
    msg_type = f"chapter_{trigger}"
    try:
        redis_conn = get_redis_connection("default")
        message = {
            "type": msg_type,
            "chapter_id": str(chapter.id),
            "timestamp": str(now().timestamp()),
        }
        if changed_fields:
            message["changed_fields"] = json.dumps(changed_fields)

        redis_conn.xadd(STREAM_KEY, message)
        logger.info("Published %s notification for chapter %s", msg_type, chapter.id)
    except Exception:
        logger.exception(
            "Failed to publish %s notification for chapter %s",
            msg_type,
            chapter.id,
        )


def publish_event_notification(
    event: Event,
    trigger: str,
    days_remaining: int | None = None,
    changed_fields: dict | None = None,
) -> None:
    """Publish a notification for an event creation, update, or deadline reminder.

    Args:
        event: The Event instance.
        trigger: Either "created", "updated", or "deadline_reminder".
        days_remaining: Days until event (only for deadline_reminder).
        changed_fields: Dict of changed fields with old/new values (only for updates).

    """
    msg_type = f"event_{trigger}"
    try:
        redis_conn = get_redis_connection("default")
        message = {
            "type": msg_type,
            "event_id": str(event.id),
            "timestamp": str(now().timestamp()),
        }
        if days_remaining is not None:
            message["days_remaining"] = str(days_remaining)
        if changed_fields:
            message["changed_fields"] = json.dumps(changed_fields)

        redis_conn.xadd(STREAM_KEY, message)
        logger.info("Published %s notification for event %s", msg_type, event.id)
    except Exception:
        logger.exception(
            "Failed to publish %s notification for event %s",
            msg_type,
            event.id,
        )


def send_notification(*, user, title, message, notification_type, related_link):
    """Send notification to user and persist to DB."""
    if Notification.objects.filter(
        recipient_id=user.id,
        type=notification_type,
        related_link=related_link,
        message=message,
    ).exists():
        logger.info("Already notified %s for %s, skipping", user.email, notification_type)
        return

    full_message = f"{message}\n\nView: {related_link}" if related_link else message
    send_mail(
        subject=title,
        message=full_message,
        from_email="noreply@owasp.org",
        recipient_list=[user.email],
        fail_silently=False,
    )
    logger.info("Sent %s email to %s", notification_type, user.email)

    Notification.objects.create(
        recipient=user,
        type=notification_type,
        title=title,
        message=message,
        related_link=related_link,
    )
