"""Abstract base class for email service providers."""

from abc import ABC, abstractmethod


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

        """

    @abstractmethod
    def send_bulk(self, messages: list[dict]) -> dict:
        """Send multiple emails.

        Args:
            messages: List of dicts, each containing 'to', 'subject',
                     'html_body', and 'plain_body' keys.

        Returns:
            Dict with 'sent' and 'failed' counts.

        """
