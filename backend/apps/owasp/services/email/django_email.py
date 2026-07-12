"""Django email service implementation."""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

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
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to],
            headers=headers,
        )
        msg.attach_alternative(html_body, "text/html")
        sent_count = msg.send()
        return sent_count > 0

    def send_bulk(self, messages: list[dict]) -> dict:
        """Send multiple emails, tracking success/failure counts."""
        results = {"sent": 0, "failed": 0}

        for message in messages:
            try:
                success = self.send(
                    to=message["to"],
                    subject=message["subject"],
                    html_body=message["html_body"],
                    plain_body=message["plain_body"],
                    headers=message.get("headers"),
                )
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            except Exception:
                logger.exception("Failed to send email to %s", message.get("to"))
                results["failed"] += 1

        return results
