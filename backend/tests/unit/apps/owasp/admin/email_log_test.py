"""Tests for email log admin."""

from unittest.mock import MagicMock

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.email_log import EmailLogAdmin
from apps.owasp.models.email_log import EmailLog


class TestEmailLogAdmin:
    """Test EmailLogAdmin configuration."""

    def test_model_is_registered(self):
        """Test admin package wiring registers the model."""
        assert EmailLog in admin.site._registry
        assert isinstance(admin.site._registry[EmailLog], EmailLogAdmin)

    def test_admin_configuration(self):
        """Test admin configuration matches expected setup."""
        site = AdminSite()
        admin_instance = EmailLogAdmin(EmailLog, site)

        assert "get_user" in admin_instance.list_display
        assert "snapshot" in admin_instance.list_display
        assert "status" in admin_instance.list_display
        assert admin_instance.list_filter == ("status", "created_at")

    def test_has_no_add_permission(self):
        """Test admin prevents manual creation."""
        site = AdminSite()
        admin_instance = EmailLogAdmin(EmailLog, site)
        request = MagicMock()

        assert admin_instance.has_add_permission(request) is False

    def test_readonly_fields(self):
        """Test all fields are readonly."""
        site = AdminSite()
        admin_instance = EmailLogAdmin(EmailLog, site)

        assert "snapshot_subscription" in admin_instance.readonly_fields
        assert "snapshot" in admin_instance.readonly_fields
        assert "status" in admin_instance.readonly_fields
        assert "error_message" in admin_instance.readonly_fields

    def test_get_user_with_subscription(self):
        """Test get_user returns user from snapshot subscription."""
        site = AdminSite()
        admin_instance = EmailLogAdmin(EmailLog, site)

        obj = MagicMock(spec=EmailLog)
        obj.snapshot_subscription = MagicMock()
        obj.snapshot_subscription.user = "snapshot_user"

        assert admin_instance.get_user(obj) == "snapshot_user"

    def test_get_user_no_subscription(self):
        """Test get_user returns dash when no subscription set."""
        site = AdminSite()
        admin_instance = EmailLogAdmin(EmailLog, site)

        obj = MagicMock(spec=EmailLog)
        obj.snapshot_subscription = None

        assert admin_instance.get_user(obj) == "—"
