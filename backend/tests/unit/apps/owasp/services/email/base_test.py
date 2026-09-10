"""Tests for email service base class."""

import pytest

from apps.owasp.services.email.base import EmailService


class TestEmailServiceBase:
    """Test EmailService abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test EmailService cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmailService()

    def test_send_is_abstract(self):
        """Test send is an abstract method."""
        assert hasattr(EmailService.send, "__isabstractmethod__")
        assert EmailService.send.__isabstractmethod__

    def test_send_bulk_is_abstract(self):
        """Test send_bulk is an abstract method."""
        assert hasattr(EmailService.send_bulk, "__isabstractmethod__")
        assert EmailService.send_bulk.__isabstractmethod__
