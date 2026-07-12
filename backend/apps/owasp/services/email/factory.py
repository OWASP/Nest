"""Email service factory."""

from apps.owasp.services.email.base import EmailService
from apps.owasp.services.email.django_email import DjangoEmailService


def get_email_service() -> EmailService:
    """Return the configured email service.

    Currently returns DjangoEmailService, which works with any
    Django EMAIL_BACKEND (console, SMTP, AWS SES).

    To add a new provider, create a new EmailService subclass
    and add a settings-based switch here.
    """
    return DjangoEmailService()
