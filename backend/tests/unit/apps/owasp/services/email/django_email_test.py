"""Tests for Django email service implementation."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.owasp.services.email.django_email import DjangoEmailService


class TestDjangoEmailService:
    """Test DjangoEmailService implementation."""

    @pytest.fixture
    def service(self):
        """Return DjangoEmailService instance."""
        return DjangoEmailService()

    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_success(self, mock_email_class, service):
        """Test successful email sending."""
        mock_msg = MagicMock()
        mock_msg.send.return_value = 1
        mock_email_class.return_value = mock_msg

        result = service.send(
            to="test@example.com",
            subject="Test Subject",
            html_body="<h1>Hello</h1>",
            plain_body="Hello",
        )

        assert result is True
        mock_email_class.assert_called_once()
        call_kwargs = mock_email_class.call_args[1]
        assert call_kwargs["from_email"] == settings.DEFAULT_FROM_EMAIL
        assert call_kwargs["to"] == ["test@example.com"]
        mock_msg.attach_alternative.assert_called_once_with("<h1>Hello</h1>", "text/html")
        mock_msg.send.assert_called_once()

    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_failure(self, mock_email_class, service):
        """Test email sending failure."""
        mock_msg = MagicMock()
        mock_msg.send.return_value = 0
        mock_email_class.return_value = mock_msg

        result = service.send(
            to="test@example.com",
            subject="Test Subject",
            html_body="<h1>Hello</h1>",
            plain_body="Hello",
        )

        assert result is False

    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_with_headers(self, mock_email_class, service):
        """Test sending email with custom headers."""
        mock_msg = MagicMock()
        mock_msg.send.return_value = 1
        mock_email_class.return_value = mock_msg
        headers = {"List-Unsubscribe": "<https://example.com/unsub>"}

        service.send(
            to="test@example.com",
            subject="Test",
            html_body="<p>Hi</p>",
            plain_body="Hi",
            headers=headers,
        )

        call_kwargs = mock_email_class.call_args[1]
        assert call_kwargs["headers"] == headers

    @patch("apps.owasp.services.email.django_email.get_connection")
    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_bulk_all_success(self, mock_email_class, mock_get_conn, service):
        """Test bulk sending with all emails succeeding."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_msg = MagicMock()
        mock_msg.send.return_value = 1
        mock_email_class.return_value = mock_msg

        messages = [
            {
                "to": "a@example.com",
                "subject": "Subject A",
                "html_body": "<p>A</p>",
                "plain_body": "A",
            },
            {
                "to": "b@example.com",
                "subject": "Subject B",
                "html_body": "<p>B</p>",
                "plain_body": "B",
            },
        ]

        results = service.send_bulk(messages)

        assert results == {"sent": 2, "failed": 0}
        mock_conn.open.assert_called_once()
        mock_conn.close.assert_called_once()
        assert mock_email_class.call_count == 2
        for call in mock_email_class.call_args_list:
            assert call[1]["connection"] is mock_conn

    @patch("apps.owasp.services.email.django_email.get_connection")
    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_bulk_with_failures(self, mock_email_class, mock_get_conn, service):
        """Test bulk sending with some emails failing."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_msg = MagicMock()
        mock_msg.send.side_effect = [1, 0, 1]
        mock_email_class.return_value = mock_msg

        messages = [
            {"to": "a@ex.com", "subject": "A", "html_body": "<p>A</p>", "plain_body": "A"},
            {"to": "b@ex.com", "subject": "B", "html_body": "<p>B</p>", "plain_body": "B"},
            {"to": "c@ex.com", "subject": "C", "html_body": "<p>C</p>", "plain_body": "C"},
        ]

        results = service.send_bulk(messages)

        assert results == {"sent": 2, "failed": 1}
        mock_conn.close.assert_called_once()

    @patch("apps.owasp.services.email.django_email.get_connection")
    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_bulk_with_exception(self, mock_email_class, mock_get_conn, service):
        """Test bulk sending when exception occurs."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_msg = MagicMock()
        mock_msg.send.side_effect = [1, Exception("SMTP Error")]
        mock_email_class.return_value = mock_msg

        messages = [
            {"to": "a@ex.com", "subject": "A", "html_body": "<p>A</p>", "plain_body": "A"},
            {"to": "b@ex.com", "subject": "B", "html_body": "<p>B</p>", "plain_body": "B"},
        ]

        results = service.send_bulk(messages)

        assert results == {"sent": 1, "failed": 1}
        mock_conn.close.assert_called_once()

    @patch("apps.owasp.services.email.django_email.get_connection")
    @patch("apps.owasp.services.email.django_email.EmailMultiAlternatives")
    def test_send_bulk_empty_list(self, mock_email_class, mock_get_conn, service):
        """Test bulk sending with empty message list."""
        results = service.send_bulk([])

        assert results == {"sent": 0, "failed": 0}
        mock_email_class.assert_not_called()
        mock_get_conn.assert_not_called()

    @patch("apps.owasp.services.email.django_email.get_connection")
    def test_send_bulk_connection_failure(self, mock_get_conn, service):
        """Test bulk sending when connection fails to open."""
        mock_conn = MagicMock()
        mock_conn.open.side_effect = Exception("Connection refused")
        mock_get_conn.return_value = mock_conn

        messages = [
            {"to": "a@ex.com", "subject": "A", "html_body": "<p>A</p>", "plain_body": "A"},
            {"to": "b@ex.com", "subject": "B", "html_body": "<p>B</p>", "plain_body": "B"},
        ]

        results = service.send_bulk(messages)

        assert results == {"sent": 0, "failed": 2}
