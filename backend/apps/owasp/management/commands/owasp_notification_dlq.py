"""Management command to manage notification DLQ."""

import sys

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

from apps.nest.models import User
from apps.owasp.utils.notifications import send_notification


class Command(BaseCommand):
    """Manage notification DLQ manually."""

    help = "Manage notification DLQ: list, retry, or remove failed notifications"

    DLQ_STREAM_KEY = "owasp_notifications_dlq"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            type=str,
            choices=["list", "retry", "remove"],
            help="Action to perform: list, retry, or remove",
        )
        parser.add_argument(
            "--id",
            type=str,
            help="Specific message ID to act on (required for retry/remove unless --all is used)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Apply action to all messages",
        )

    def handle(self, *args, **options):
        action = options["action"]
        message_id = options.get("id")
        all_messages = options.get("all")

        redis_conn = get_redis_connection("default")

        if action == "list":
            self.list_dlq(redis_conn)
        elif action == "retry":
            if not message_id and not all_messages:
                self.stdout.write(self.style.ERROR("Error: --id or --all is required for retry"))
                sys.exit(1)
            self.retry_dlq(redis_conn, message_id, all_messages)
        elif action == "remove":
            if not message_id and not all_messages:
                self.stdout.write(self.style.ERROR("Error: --id or --all is required for remove"))
                sys.exit(1)
            self.remove_dlq(redis_conn, message_id, all_messages)

    def list_dlq(self, redis_conn):
        """List all failed notifications in DLQ."""
        messages = redis_conn.xrange(self.DLQ_STREAM_KEY, "-", "+")

        if not messages:
            self.stdout.write(self.style.SUCCESS("DLQ is empty - no failed notifications"))
            return

        self.stdout.write("\n" + "=" * 100)
        self.stdout.write(
            f"{'ID':<20} | {'Email':<25} | {'Type':<18} | {'Entity':<15} | {'Retries':<8}"
        )
        self.stdout.write("=" * 100)

        for msg_id, data in messages:
            msg_id_str = msg_id.decode("utf-8") if isinstance(msg_id, bytes) else msg_id
            user_email = self._get_value(data, b"user_email", "unknown")
            notif_type = self._get_value(data, b"notification_type", "unknown")
            entity_name = self._get_value(data, b"entity_name", "unknown")[:15]
            retries = self._get_value(data, b"dlq_retries", "0")

            self.stdout.write(
                f"{msg_id_str:<20} | {user_email:<25} | "
                f"{notif_type:<18} | {entity_name:<15} | {retries:<8}"
            )

        self.stdout.write("=" * 100)
        self.stdout.write(f"Total: {len(messages)} failed notification(s)\n")

    def retry_dlq(self, redis_conn, message_id, all_messages):
        """Retry failed notification(s)."""
        if all_messages:
            messages = redis_conn.xrange(self.DLQ_STREAM_KEY, "-", "+")
        else:
            result = redis_conn.xrange(self.DLQ_STREAM_KEY, message_id, message_id)
            messages = result or []

        if not messages:
            self.stdout.write(self.style.ERROR("Message(s) not found"))
            return

        success_count = 0
        error_count = 0

        for msg_id, data in messages:
            if not data:
                continue

            try:
                user_email = self._get_value(data, b"user_email")
                title = self._get_value(data, b"title")
                message = self._get_value(data, b"message")
                related_link = self._get_value(data, b"related_link")

                user_id = self._get_value(data, b"user_id")
                notification_type = self._get_value(data, b"notification_type")

                if user_email and title and message:
                    if user_id and notification_type:
                        try:
                            user = User.objects.get(id=int(user_id))
                            send_notification(
                                user=user,
                                title=title,
                                message=message,
                                notification_type=notification_type,
                                related_link=related_link or "",
                            )
                        except User.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(f"User {user_id} not found: {msg_id}")
                            )
                            error_count += 1
                            continue
                    else:
                        # Fallback for old DLQ format
                        full_message = (
                            f"{message}\n\nView: {related_link}" if related_link else message
                        )
                        send_mail(
                            subject=title,
                            message=full_message,
                            from_email="noreply@owasp.org",
                            recipient_list=[user_email],
                            fail_silently=False,
                        )

                    redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                    success_count += 1
                    self.stdout.write(f"Retried: {msg_id} -> {user_email}")
                else:
                    self.stdout.write(self.style.WARNING(f"Skipped (missing data): {msg_id}"))
                    error_count += 1

            except Exception as e:  # noqa: BLE001
                error_count += 1
                retries = int(self._get_value(data, b"dlq_retries", "0"))
                new_retries = str(retries + 1)
                data[b"dlq_retries"] = new_retries.encode()
                new_msg = {k.decode(): v.decode() for k, v in data.items()}
                redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
                redis_conn.xadd(self.DLQ_STREAM_KEY, new_msg)
                self.stdout.write(
                    self.style.ERROR(f"Failed to retry {msg_id}: {e}, incremented retries")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nRetry complete: {success_count} succeeded, {error_count} failed/retried"
            )
        )

    def remove_dlq(self, redis_conn, message_id, all_messages):
        """Remove failed notification(s) from DLQ."""
        if all_messages:
            messages = redis_conn.xrange(self.DLQ_STREAM_KEY, "-", "+")
        else:
            messages = redis_conn.xrange(self.DLQ_STREAM_KEY, message_id, message_id)

        if not messages:
            self.stdout.write(self.style.ERROR("No messages found"))
            return

        count = 0
        for msg_id, _ in messages:
            redis_conn.xdel(self.DLQ_STREAM_KEY, msg_id)
            count += 1
            self.stdout.write(f"Removed: {msg_id}")

        self.stdout.write(self.style.SUCCESS(f"\nRemoved {count} message(s) from DLQ"))

    def _get_value(self, data, key, default=None):
        """Get value from message data."""
        value = data.get(key.encode() if isinstance(key, str) else key)
        if value:
            return value.decode("utf-8")
        return default
