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
        try:
            snapshot_id = int(data.get(b"snapshot_id").decode("utf-8"))
            snapshot = Snapshot.objects.get(id=snapshot_id)
            
            users = User.objects.filter(is_active=True)
            
            if not users.exists():
                logger.info("No active users found.")
                return

            logger.info(f"Sending snapshot notification to {users.count()} users")
            
            for user in users:
                self.send_notification(user, snapshot)

        except Snapshot.DoesNotExist:
            logger.error(f"Snapshot matching ID {snapshot_id} not found.")
        except Exception:
            logger.exception("Error handling snapshot published event")

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
        try:
            send_mail(
                subject=title,
                message=message,
                from_email="noreply@owasp.org",
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Sent email to {user.email}")
        except Exception:
            logger.exception(f"Failed to send email to {user.email}")
