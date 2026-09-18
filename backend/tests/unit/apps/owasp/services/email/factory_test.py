"""Tests for email service factory."""

from apps.owasp.services.email.base import EmailService
from apps.owasp.services.email.django_email import DjangoEmailService
from apps.owasp.services.email.factory import get_email_service


class TestEmailServiceFactory:
    """Test email service factory."""

    def test_returns_django_email_service(self):
        """Test factory returns DjangoEmailService."""
        service = get_email_service()
        assert isinstance(service, DjangoEmailService)

    def test_returns_email_service_subclass(self):
        """Test factory returns an EmailService subclass."""
        service = get_email_service()
        assert isinstance(service, EmailService)

    def test_returns_new_instance_each_call(self):
        """Test factory returns new instance each call."""
        service1 = get_email_service()
        service2 = get_email_service()
        assert service1 is not service2
