"""Abstract base class for email service providers."""

from abc import ABC, abstractmethod
from smtplib import SMTPException

EMAIL_SEND_ERRORS = (
    OSError,
    SMTPException,
    UnicodeEncodeError,
    ValueError,
)


class EmailService(ABC):
    """Abstract email service provider.

    Provides an abstraction layer that makes it easy to switch between
    email sending service providers (e.g., Django SMTP, AWS SES, Resend).
    """

    @abstractmethod
    def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        plain_body: str,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """Send a single email.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: HTML version of the email body.
            plain_body: Plain text version of the email body.
            headers: Optional custom email headers.

        Returns:
            True if the email was sent successfully.

        Raises:
            Exception: Implementations must raise appropriate exceptions (like
                SMTPException or OSError) if sending fails, allowing the caller
                to handle the error.

        """

    @abstractmethod
    def send_bulk(self, messages: list[dict]) -> dict:
        """Send multiple emails.

        Unlike `send()`, this method must catch individual email sending errors
        and report them in the `failed` count rather than raising exceptions.

        Args:
            messages: List of dicts, each containing 'to', 'subject',
                     'html_body', 'plain_body', and optionally 'headers' keys.

        Returns:
            Dict with 'sent' and 'failed' counts.

        """
