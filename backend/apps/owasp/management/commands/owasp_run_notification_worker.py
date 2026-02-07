"""Management command to run notification worker."""

import contextlib
import logging
import os
import socket
import time

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

from apps.nest.models import User
from apps.owasp.models.notification import Notification
from apps.owasp.models.snapshot import Snapshot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run notification worker."""

    help = "Run notification worker to process Redis stream messages."

    # Retry configuration
    MAX_RETRIES = 5
    BASE_DELAY = 2  # seconds
    DELAY_MULTIPLIER = 2
    MAX_DLQ_RETRIES = 5
    DLQ_STREAM_KEY = "owasp_notifications_dlq"
    DLQ_CHECK_INTERVAL = 300  # seconds

    def handle(self, *args, **options):
        """Handle execution."""
        self.stdout.write("Starting notification worker...")
        redis_conn = get_redis_connection("default")
        stream_key = "owasp_notifications"
        group_name = "notification_group"
        consumer_name = f"{socket.gethostname()}_{os.getpid()}"

        self.ensure_consumer_group(redis_conn, stream_key, group_name)

        self.recover_pending_messages(redis_conn, stream_key, group_name, consumer_name)

        last_dlq_check = time.time()

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
                if events:
                    for _, messages in events:
                        for message_id, data in messages:
                            try:
                                self.process_message(data)
                                # Explicitly acknowledge the message
                                redis_conn.xack(stream_key, group_name, message_id)
                                logger.info("Message processed successfully.")
                            except Exception:
                                logger.exception("Error processing message %s", message_id)

                # Check DLQ every 300 seconds
                if time.time() - last_dlq_check > self.DLQ_CHECK_INTERVAL:
                    self.process_dlq(redis_conn)
                    last_dlq_check = time.time()

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
        if msg_type == "snapshot_published":
            self.handle_snapshot_published(data)

    def handle_snapshot_published(self, data):
        """Handle snapshot published event."""
        redis_conn = get_redis_connection("default")

        try:
            raw_id = data.get(b"snapshot_id")
            if not raw_id:
                return
            snapshot_id = int(raw_id.decode("utf-8"))
            snapshot = Snapshot.objects.get(id=snapshot_id)

            users = User.objects.filter(is_active=True)

            if not users.exists():
                logger.info("No active users found.")
                return

            logger.info("Sending snapshot notification to %d users", users.count())

            failed_users = []

            for user in users:
                success = self.send_notification_with_retry(user, snapshot)
                if not success:
                    failed_users.append(
                        {
                            "user_id": str(user.id),
                            "email": user.email,
                            "snapshot_id": str(snapshot_id),
                        }
                    )

            # Send failed users to DLQ
            if failed_users:
                for failed_user in failed_users:
                    dlq_message = {
                        "type": "failed_notification",
                        "user_id": failed_user["user_id"],
                        "snapshot_id": failed_user["snapshot_id"],
                        "timestamp": str(time.time()),
                        "dlq_retries": "0",
                    }
                    redis_conn.xadd(self.DLQ_STREAM_KEY, dlq_message)

                logger.warning("Sent %d failed notifications to DLQ", len(failed_users))

        except Snapshot.DoesNotExist:
            logger.exception("Snapshot matching ID %s not found.", snapshot_id)
        except Exception:
            logger.exception("Error handling snapshot published event")

    def send_notification_with_retry(self, user, snapshot):
        """Send notification with exponential backoff retry logic."""
        retry_count = 0
        last_error = None

        while retry_count <= self.MAX_RETRIES:
            try:
                self.send_notification(user, snapshot)
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

    def send_notification(self, user, snapshot):
        """Send notification to user."""
        title = f"New Snapshot Published: {snapshot.title}"
        related_link = f"{settings.SITE_URL}/community/snapshots/{snapshot.id}"

        if Notification.objects.filter(
            recipient_id=user.id,
            type="snapshot_published",
            related_link=related_link,
        ).exists():
            logger.info("Already notified %s for this snapshot, skipping", user.email)
            return

        message = f"Check out the latest OWASP snapshot: {snapshot.title}"

        # Send Email
        send_mail(
            subject=title,
            message=message,
            from_email="noreply@owasp.org",
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Sent email to %s", user.email)

        # Create DB record
        Notification.objects.create(
            recipient=user,
            type="snapshot_published",
            title=title,
            message=message,
            related_link=related_link,
        )

    def process_dlq(self, redis_conn):
        """Process messages from DLQ - retry failed notifications."""
        lock = redis_conn.lock("owasp_notifications_dlq_lock", timeout=600, blocking=False)
        if not lock.acquire():
            return

        try:
            self.stdout.write("Checking DLQ for failed notifications...")
            messages = redis_conn.xrange(self.DLQ_STREAM_KEY, "-", "+", count=50)

            if not messages:
                self.stdout.write("No messages in DLQ")
                return

            processed_count = 0
            failed_count = 0

            for msg_id, data in messages:
                try:
                    dlq_retries = 0
                    msg_type = (data.get(b"type") or b"").decode("utf-8")
                    if msg_type == "recovery_failed":
                        logger.error(
                            "Permanent recovery failure for message %s: %s",
                            (data.get(b"message_id") or b"unknown").decode("utf-8"),
                            (data.get(b"error") or b"unknown").decode("utf-8"),
                        )
                        redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                        continue

                    raw_dlq_retries = data.get(b"dlq_retries", b"0")
                    try:
                        dlq_retries = int(raw_dlq_retries.decode("utf-8"))
                    except (ValueError, AttributeError):
                        dlq_retries = 0
                    raw_user_id = data.get(b"user_id")
                    raw_snapshot_id = data.get(b"snapshot_id")

                    if not raw_user_id or not raw_snapshot_id:
                        logger.warning("DLQ message %s missing required fields, removing", msg_id)
                        redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                        continue

                    user_id = int(raw_user_id.decode("utf-8"))
                    snapshot_id = int(raw_snapshot_id.decode("utf-8"))

                    user = User.objects.get(id=user_id)
                    snapshot = Snapshot.objects.get(id=snapshot_id)

                    self.send_notification(user, snapshot)
                    redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                    processed_count += 1
                    logger.info(
                        "Successfully reprocessed notification for user %s",
                        user.email,
                    )

                except ObjectDoesNotExist:
                    logger.warning("User or snapshot not found, removing from DLQ")
                    redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                    failed_count += 1
                except Exception:
                    failed_count += 1
                    dlq_retries += 1

                    if dlq_retries > self.MAX_DLQ_RETRIES:
                        redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                        logger.exception(
                            "DLQ message %s exceeded max retries (%d). Dropping.",
                            msg_id,
                            self.MAX_DLQ_RETRIES,
                        )
                    else:
                        new_data = {k.decode("utf-8"): v.decode("utf-8") for k, v in data.items()}
                        new_data["dlq_retries"] = str(dlq_retries)
                        redis_conn.xadd(self.DLQ_STREAM_KEY, new_data)
                        redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                        logger.warning(
                            "Failed to reprocess DLQ message %s (attempt %d/%d). Re-queued.",
                            msg_id,
                            dlq_retries,
                            self.MAX_DLQ_RETRIES,
                        )

            logger.info(
                "DLQ processing complete: %d successful, %d failed",
                processed_count,
                failed_count,
            )

        except Exception:
            logger.exception("Error processing DLQ")
        finally:
            with contextlib.suppress(Exception):
                lock.release()

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
                        redis_conn.xadd(
                            self.DLQ_STREAM_KEY,
                            {
                                "type": "recovery_failed",
                                "message_id": str(message_id),
                                "error": str(exc),
                            },
                        )
                        redis_conn.xack(stream_key, group_name, message_id)
            else:
                self.stdout.write("No stuck messages found.")
        except Exception:
            logger.exception("Error checking PEL for stuck messages")
