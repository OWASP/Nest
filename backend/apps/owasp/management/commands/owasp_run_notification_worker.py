"""Management command to run notification worker."""

import logging
import time

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
    DLQ_STREAM_KEY = "owasp_notifications_dlq"

    def handle(self, *args, **options):
        """Handle execution."""
        self.stdout.write("Starting notification worker...")
        redis_conn = get_redis_connection("default")
        stream_key = "owasp_notifications"
        group_name = "notification_group"
        consumer_name = "worker_1"

        # Create consumer group if it doesn't exist
        try:
            redis_conn.xgroup_create(stream_key, group_name, id="0", mkstream=True)
            print("Consumer group created successfully.")
        except Exception:
            # Group likely already exists
            pass

        while True:
            try:
                # Read new messages specifically for this group
                # ">" means "messages never delivered to other consumers so far"
                events = redis_conn.xreadgroup(group_name, consumer_name, {stream_key: ">"}, count=1, block=5000)
                print("Events: ", events)
                if not events:
                    continue

                for _, messages in events:
                    for message_id, data in messages:
                        try:
                            self.process_message(data)
                            # Explicitly acknowledge the message
                            redis_conn.xack(stream_key, group_name, message_id)
                            print("Message processed successfully.")
                        except Exception:
                            logger.exception(f"Error processing message {message_id}")

            except Exception:
                logger.exception("Error reading from stream group")
                time.sleep(1)

    def process_message(self, data):
        """Process a single message from the stream."""
        msg_type = data.get(b"type", b"").decode("utf-8")
        if msg_type == "snapshot_published":
            self.handle_snapshot_published(data)

    def handle_snapshot_published(self, data):
        """Handle snapshot published event."""
        redis_conn = get_redis_connection("default")
        
        try:
            snapshot_id = int(data.get(b"snapshot_id").decode("utf-8"))
            snapshot = Snapshot.objects.get(id=snapshot_id)
            
            users = User.objects.filter(is_active=True)
            
            if not users.exists():
                logger.info("No active users found.")
                return

            logger.info(f"Sending snapshot notification to {users.count()} users")
            
            failed_users = []
            
            for user in users:
                success = self.send_notification_with_retry(user, snapshot)
                if not success:
                    failed_users.append({
                        'user_id': str(user.id),
                        'email': user.email,
                        'snapshot_id': str(snapshot_id)
                    })
            
            # Send failed users to DLQ
            if failed_users:
                for failed_user in failed_users:
                    dlq_message = {
                        'type': 'failed_notification',
                        'user_id': failed_user['user_id'],
                        'email': failed_user['email'],
                        'snapshot_id': failed_user['snapshot_id'],
                        'retry_count': str(self.MAX_RETRIES),
                        'timestamp': str(time.time()),
                        'last_attempt': str(time.time())
                    }
                    redis_conn.xadd(self.DLQ_STREAM_KEY, dlq_message)
                
                logger.warning(f"Sent {len(failed_users)} failed notifications to DLQ")

        except Snapshot.DoesNotExist:
            logger.error(f"Snapshot matching ID {snapshot_id} not found.")
        except Exception:
            logger.exception("Error handling snapshot published event")

    def send_notification_with_retry(self, user, snapshot):
        """Send notification with exponential backoff retry logic."""
        retry_count = 0
        last_error = None
        
        while retry_count <= self.MAX_RETRIES:
            try:
                self.send_notification(user, snapshot)
                if retry_count > 0:
                    logger.info(f"Email to {user.email} succeeded after {retry_count} retries")
                return True
            except Exception as e:
                retry_count += 1
                last_error = e
                if retry_count <= self.MAX_RETRIES:
                    delay = self.BASE_DELAY * (self.DELAY_MULTIPLIER ** (retry_count - 1))
                    logger.warning(
                        f"Email to {user.email} failed (attempt {retry_count}/{self.MAX_RETRIES}). "
                        f"Retrying in {delay}s. Error: {str(e)}"
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Email to {user.email} failed after {self.MAX_RETRIES} retries. "
                        f"Error: {str(last_error)}"
                    )
                    return False
        
        return False

    def send_notification(self, user, snapshot):
        """Send notification to user."""
        title = f"New Snapshot Published: {snapshot.title}"
        message = f"Check out the latest OWASP snapshot: {snapshot.title}"
        
        # Create DB record
        Notification.objects.create(
            recipient=user,
            type="snapshot_published",
            title=title,
            message=message,
        )

        # Send Email
        send_mail(
            subject=title,
            message=message,
            from_email="noreply@owasp.org",
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Sent email to {user.email}")
