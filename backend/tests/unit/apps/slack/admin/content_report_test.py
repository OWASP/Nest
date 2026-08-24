from django.contrib.admin.sites import AdminSite
from django.test import override_settings

from apps.slack.admin.content_report import ContentReportAdmin
from apps.slack.models.content_report import ContentReport


class TestContentReportAdmin:
    def test_reports_are_read_only_records(self):
        """Test content report records cannot be manually created in admin."""
        admin = ContentReportAdmin(model=ContentReport, admin_site=AdminSite())

        assert not admin.has_add_permission(request=None)
        assert admin.readonly_fields == (
            "conversation",
            "message",
            "message_ts",
            "report_type",
            "source",
            "reaction_count",
            "reporter_user_ids",
            "alert_message_ts",
        )

    @override_settings(IS_LOCAL_ENVIRONMENT=False)
    def test_delete_disabled_outside_local(self):
        """Test content report deletion is blocked outside the local environment."""
        admin = ContentReportAdmin(model=ContentReport, admin_site=AdminSite())

        assert not admin.has_delete_permission(request=None)

    @override_settings(IS_LOCAL_ENVIRONMENT=True)
    def test_delete_allowed_in_local(self):
        """Test content report deletion is allowed in the local environment."""
        admin = ContentReportAdmin(model=ContentReport, admin_site=AdminSite())

        assert admin.has_delete_permission(request=None)
