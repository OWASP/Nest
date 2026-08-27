"""Django email service implementation."""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection

from apps.owasp.services.email.base import EmailService

logger = logging.getLogger(__name__)


class DjangoEmailService(EmailService):
    """Email service using Django's EMAIL_BACKEND.

    Works with any Django email backend including:
    - Console (local dev)
    - SMTP
    - AWS SES (via django-ses)
    """

    def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        plain_body: str,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """Send a single email using Django's EmailMultiAlternatives."""
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to],
                headers=headers,
            )
            msg.attach_alternative(html_body, "text/html")
            sent_count = msg.send()
        except Exception:
            logger.exception("Failed to send email to %s", to)
            return False
        return sent_count > 0

    def _close_connection_safely(self, connection) -> None:
        """Safely close the email connection, logging any exceptions."""
        if connection:
            try:
                connection.close()
            except Exception:
                logger.exception("Failed to close email connection")

    def send_bulk(self, messages: list[dict]) -> dict:
        """Send multiple emails using a single shared connection."""
        results = {"sent": 0, "failed": 0}
        if not messages:
            return results

        connection = None
        try:
            connection = get_connection()
            connection.open()
        except Exception:
            logger.exception("Failed to open email connection")
            self._close_connection_safely(connection)
            return {"sent": 0, "failed": len(messages)}

        try:
            for message in messages:
                try:
                    msg = EmailMultiAlternatives(
                        subject=message["subject"],
                        body=message["plain_body"],
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[message["to"]],
                        headers=message.get("headers"),
                        connection=connection,
                    )
                    msg.attach_alternative(message["html_body"], "text/html")
                    if msg.send() > 0:
                        results["sent"] += 1
                    else:
                        results["failed"] += 1
                except Exception:
                    logger.exception("Failed to send email to %s", message.get("to"))
                    results["failed"] += 1
        finally:
            self._close_connection_safely(connection)

        return results
