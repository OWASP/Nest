"""Management command to run notification worker."""

import json
import logging
import os
import socket
import time

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.event import Event
from apps.owasp.models.notification import Subscription
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.utils.notifications import send_notification

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run notification worker."""

    help = "Run notification worker to process Redis stream messages."

    # Retry configuration
    MAX_RETRIES = 5
    BASE_DELAY = 2  # seconds
    DELAY_MULTIPLIER = 2
    DLQ_STREAM_KEY = "owasp_notifications_dlq"

    def handle(self, *args, **options):
        """Handle execution."""
        self.stdout.write("Starting notification worker...")
        redis_conn = get_redis_connection("default")
        stream_key = "owasp_notifications"
        group_name = "notification_group"
        consumer_name = f"{socket.gethostname()}_{os.getpid()}"

        self.ensure_consumer_group(redis_conn, stream_key, group_name)

        self.recover_pending_messages(redis_conn, stream_key, group_name, consumer_name)

        while True:
            try:
                # Read new messages specifically for this group
                # ">" means "messages never delivered to other consumers so far"
                events = redis_conn.xreadgroup(
                    group_name,
                    consumer_name,
                    {stream_key: ">"},
                    count=1,
                    block=5000,
                )
                # Process main stream messages
                logger.info("event: %s", events)
                if events:
                    for _, messages in events:
                        for message_id, data in messages:
                            try:
                                self.process_message(data)
                                # Explicitly acknowledge the message
                                redis_conn.xack(stream_key, group_name, message_id)
                                logger.info("Message processed successfully.")
                            except Exception as exc:
                                logger.exception("Error processing message %s", message_id)
                                try:
                                    dlq_entry = {k.decode(): v.decode() for k, v in data.items()}
                                    dlq_entry.update(
                                        {
                                            "type": "processing_failed",
                                            "original_message_id": message_id.decode()
                                            if isinstance(message_id, bytes)
                                            else str(message_id),
                                            "error": str(exc),
                                            "dlq_retries": "0",
                                        }
                                    )
                                    redis_conn.xadd(self.DLQ_STREAM_KEY, dlq_entry)
                                    # ACK so it doesn't stay stranded in PEL
                                    redis_conn.xack(stream_key, group_name, message_id)
                                except Exception:
                                    logger.exception(
                                        "Failed to send stranded message %s to DLQ", message_id
                                    )

            except Exception as e:
                if "NOGROUP" in str(e):
                    logger.warning("Consumer group missing, attempting to recreate...")
                    self.ensure_consumer_group(redis_conn, stream_key, group_name)
                else:
                    logger.exception("Error reading from stream group")
                time.sleep(1)

    def ensure_consumer_group(self, redis_conn, stream_key, group_name):
        """Ensure the consumer group exists."""
        try:
            redis_conn.xgroup_create(stream_key, group_name, id="0", mkstream=True)
            self.stdout.write(self.style.SUCCESS(f"Consumer group '{group_name}' created."))
        except Exception as e:  # noqa: BLE001
            if "BUSYGROUP" in str(e):
                self.stdout.write(f"Consumer group '{group_name}' already exists.")
            else:
                self.stdout.write(self.style.ERROR(f"Error creating group: {e}"))

    def process_message(self, data):
        """Process a single message from the stream."""
        msg_type = data.get(b"type", b"").decode("utf-8")

        handlers = {
            "snapshot_published": self.handle_snapshot_published,
            "chapter_created": self.handle_chapter_created,
            "chapter_updated": self.handle_chapter_updated,
            "event_created": self.handle_event_created,
            "event_updated": self.handle_event_updated,
            "event_deadline_reminder": self.handle_event_deadline_reminder,
        }

        handler = handlers.get(msg_type)
        if handler:
            handler(data)
        else:
            logger.warning("Unknown message type: %s", msg_type)

    def send_notification_with_retry(
        self, *, user, title, message, notification_type, related_link
    ):
        """Send notification with exponential backoff retry logic."""
        retry_count = 0
        last_error = None

        while retry_count <= self.MAX_RETRIES:
            try:
                send_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    related_link=related_link,
                )
            except Exception as e:
                retry_count += 1
                last_error = e
                if retry_count <= self.MAX_RETRIES:
                    delay = self.BASE_DELAY * (self.DELAY_MULTIPLIER ** (retry_count - 1))
                    logger.warning(
                        "Email to %s failed (attempt %d/%d). Retrying in %ds. Error: %s",
                        user.email,
                        retry_count,
                        self.MAX_RETRIES,
                        delay,
                        last_error,
                    )
                    time.sleep(delay)
                else:
                    logger.exception(
                        "Email to %s failed after %d retries",
                        user.email,
                        self.MAX_RETRIES,
                    )
                    return False
            else:
                if retry_count > 0:
                    logger.info(
                        "Email to %s succeeded after %d retries",
                        user.email,
                        retry_count,
                    )
                return True

        return False

    def handle_snapshot_published(self, data):
        """Handle snapshot published event."""
        self._handle_entity_notification(
            data=data,
            id_field=b"snapshot_id",
            model_class=Snapshot,
            notification_type="snapshot_published",
            global_subscription=True,
        )

    def handle_chapter_created(self, data):
        """Handle chapter created event — notify 'all chapters' subscribers."""
        self._handle_entity_notification(
            data=data,
            id_field=b"chapter_id",
            model_class=Chapter,
            notification_type="chapter_created",
            global_subscription=True,
        )

    def handle_chapter_updated(self, data):
        """Handle chapter updated event — notify specific chapter subscribers."""
        self._handle_entity_notification(
            data=data,
            id_field=b"chapter_id",
            model_class=Chapter,
            notification_type="chapter_updated",
            global_subscription=False,
        )

    def handle_event_created(self, data):
        """Handle event created — notify 'all events' subscribers."""
        self._handle_entity_notification(
            data=data,
            id_field=b"event_id",
            model_class=Event,
            notification_type="event_created",
            global_subscription=True,
        )

    def handle_event_updated(self, data):
        """Handle event updated — notify specific event subscribers."""
        self._handle_entity_notification(
            data=data,
            id_field=b"event_id",
            model_class=Event,
            notification_type="event_updated",
            global_subscription=False,
        )

    def handle_event_deadline_reminder(self, data):
        """Handle event deadline reminder — notify specific event subscribers."""
        self._handle_entity_notification(
            data=data,
            id_field=b"event_id",
            model_class=Event,
            notification_type="event_deadline_reminder",
            global_subscription=False,
        )

    def _handle_entity_notification(
        self, *, data, id_field, model_class, notification_type, global_subscription=False
    ):
        """Handle entity notification for chapters, events, and snapshots.

        Args:
            data: Redis stream message data.
            id_field: The byte field name for the entity ID.
            model_class: The Django model class.
            notification_type: The notification type string.
            global_subscription: If True, query subscribers with object_id=0 (all entities).
                If False, query subscribers with object_id=entity.id (specific entity).

        """
        redis_conn = get_redis_connection("default")

        try:
            raw_id = data.get(id_field)
            if not raw_id:
                return
            entity_id = int(raw_id.decode("utf-8"))
            entity = model_class.objects.get(id=entity_id)

            content_type = ContentType.objects.get_for_model(model_class)
            subscription_filter = {
                "content_type": content_type,
                "object_id": 0 if global_subscription else entity_id,
            }
            subscriptions = Subscription.objects.filter(**subscription_filter).select_related(
                "user"
            )
            users = [sub.user for sub in subscriptions if sub.user.is_active]

            if not users:
                logger.info("No recipients found for %s.", notification_type)
                return

            logger.info("Sending %s notification to %d users", notification_type, len(users))

            entity_name = str(entity)
            entity_type = model_class.__name__.lower()

            days_bytes = data.get(b"days_remaining")
            days_info = ""
            if days_bytes:
                days = days_bytes.decode()
                days_info = f" ({days} days left)"

            changed_fields_bytes = data.get(b"changed_fields")
            changes_description = ""
            if changed_fields_bytes:
                changed_fields = json.loads(changed_fields_bytes.decode())
                changes_list = []
                for field, values in changed_fields.items():
                    old_val = values.get("old") or "empty"
                    new_val = values.get("new") or "empty"
                    field_display = field.replace("_", " ").title()
                    changes_list.append(f"{field_display}: {old_val} → {new_val}")
                changes_description = " | ".join(changes_list)

            entity_title = entity.title if hasattr(entity, "title") else entity_name

            titles = {
                "snapshot_published": f"New Snapshot Published: {entity_title}",
                "chapter_created": f"New Chapter Created: {entity_name}",
                "chapter_updated": f"Chapter Updated: {entity_name}",
                "event_created": f"New Event Published: {entity_name}",
                "event_updated": f"Event Updated: {entity_name}",
                "event_deadline_reminder": f"Event Deadline Approaching{days_info}: {entity_name}",
            }
            entity_messages = {
                "snapshot_published": f"Check out the latest OWASP snapshot: {entity_title}",
                "chapter_created": f"A new OWASP chapter has been created: {entity_name}",
                "chapter_updated": (
                    f"The OWASP chapter '{entity_name}' has been updated. "
                    f"Changes: {changes_description}"
                    if changes_description
                    else f"The OWASP chapter '{entity_name}' has been updated."
                ),
                "event_created": f"A new OWASP event has been published: {entity_name}",
                "event_updated": (
                    f"The OWASP event '{entity_name}' has been updated. "
                    f"Changes: {changes_description}"
                    if changes_description
                    else f"The OWASP event '{entity_name}' has been updated."
                ),
                "event_deadline_reminder": (
                    f"Reminder: The OWASP event '{entity_name}' "
                    f"deadline is approaching{days_info}."
                ),
            }
            url_builders = {
                "snapshot": lambda e: f"community/snapshots/{e.key}",
                "chapter": lambda e: f"chapters/{e.id}",
                "event": lambda e: f"events/{e.id}",
            }

            title = titles.get(notification_type, f"Notification: {entity_name}")
            message = entity_messages.get(notification_type, f"Update for {entity_name}")

            url_builder = url_builders.get(entity_type)
            if url_builder:
                related_link = f"{settings.SITE_URL}/{url_builder(entity)}"
            else:
                related_link = f"{settings.SITE_URL}"

            failed_users = []

            for user in users:
                success = self.send_notification_with_retry(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    related_link=related_link,
                )
                if not success:
                    failed_users.append(
                        {
                            "user": user,
                            "user_id": str(user.id),
                            "entity_type": entity_type,
                            "entity_id": str(entity_id),
                        }
                    )

            if failed_users:
                for failed_user in failed_users:
                    user_obj = failed_user.get("user")
                    dlq_message = {
                        "type": "failed_notification",
                        "notification_type": notification_type,
                        "user_id": failed_user["user_id"],
                        "user_email": user_obj.email if user_obj else "unknown",
                        "entity_type": entity_type,
                        "entity_id": str(entity_id),
                        "entity_name": entity_name,
                        "title": title,
                        "message": message,
                        "related_link": related_link,
                        "timestamp": str(time.time()),
                        "dlq_retries": "0",
                    }
                    redis_conn.xadd(self.DLQ_STREAM_KEY, dlq_message)

                logger.warning("Sent %d failed notifications to DLQ", len(failed_users))

        except model_class.DoesNotExist:
            logger.exception("%s matching ID not found.", model_class.__name__)
            raise
        except Exception:
            logger.exception("Error handling %s event", notification_type)
            raise

    def recover_pending_messages(self, redis_conn, stream_key, group_name, consumer_name):
        """Recover and reprocess stuck messages from PEL."""
        self.stdout.write("Checking for stuck messages in PEL...")
        try:
            # Claim messages idle for more than 5 minutes (300000 ms)
            result = redis_conn.xautoclaim(
                stream_key,
                group_name,
                consumer_name,
                min_idle_time=300000,  # 5 minutes
                start_id="0-0",
                count=10,
            )
            if result and result[1]:
                for message_id, data in result[1]:
                    self.stdout.write(f"Recovering stuck message: {message_id}")
                    try:
                        self.process_message(data)
                        redis_conn.xack(stream_key, group_name, message_id)
                        self.stdout.write(f"Successfully recovered message {message_id}")
                    except Exception as exc:
                        logger.exception("Failed to recover message %s", message_id)
                        dlq_entry = {k.decode(): v.decode() for k, v in data.items()}
                        dlq_entry.update(
                            {
                                "type": "recovery_failed",
                                "original_message_id": message_id.decode()
                                if isinstance(message_id, bytes)
                                else str(message_id),
                                "error": str(exc),
                                "dlq_retries": "0",
                            }
                        )
                        redis_conn.xadd(self.DLQ_STREAM_KEY, dlq_entry)
                        redis_conn.xack(stream_key, group_name, message_id)
            else:
                self.stdout.write("No stuck messages found.")
        except Exception:
            logger.exception("Error checking PEL for stuck messages")
