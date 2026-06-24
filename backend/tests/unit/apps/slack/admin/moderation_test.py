from django.contrib.admin.sites import AdminSite

from apps.slack.admin.moderation import ModerationAlertAdmin
from apps.slack.models.moderation import ModerationAlert


class TestModerationAlertAdmin:
    def test_alerts_are_read_only_records(self):
        """Test moderation alert records cannot be manually changed in admin."""
        admin = ModerationAlertAdmin(model=ModerationAlert, admin_site=AdminSite())

        assert not admin.has_add_permission(request=None)
        assert not admin.has_delete_permission(request=None)
        assert "alert_message_ts" in admin.readonly_fields
