"""Notification utils."""

import logging

from django.utils.timezone import now
from django_redis import get_redis_connection

from apps.owasp.models.snapshot import Snapshot

logger = logging.getLogger(__name__)


def publish_snapshot_notification(snapshot: Snapshot) -> None:
    """Publish a notification for a published snapshot."""
    try:
        redis_conn = get_redis_connection("default")
        stream_key = "owasp_notifications"
        message = {
            "type": "snapshot_published",
            "snapshot_id": str(snapshot.id),
            "timestamp": str(now().timestamp()),
        }
        redis_conn.xadd(stream_key, message)
        logger.info("Published snapshot notification for snapshot %s", snapshot.id)
    except Exception:
        logger.exception(
            "Failed to publish snapshot notification for snapshot %s",
            snapshot.id,
        )
