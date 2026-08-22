from django.contrib.admin.sites import AdminSite

from apps.slack.admin.content_report import ContentReportAdmin
from apps.slack.models.content_report import ContentReport


class TestContentReportAdmin:
    def test_reports_are_read_only_records(self):
        """Test content report records cannot be manually changed in admin."""
        admin = ContentReportAdmin(model=ContentReport, admin_site=AdminSite())

        assert not admin.has_add_permission(request=None)
        assert not admin.has_delete_permission(request=None)
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
