from django.contrib.admin.sites import AdminSite

from apps.slack.admin.reaction_alert import ReactionAlertAdmin
from apps.slack.models.reaction_alert import ReactionAlert


class TestReactionAlertAdmin:
    def test_alerts_are_read_only_records(self):
        """Test reaction alert records cannot be manually changed in admin."""
        admin = ReactionAlertAdmin(model=ReactionAlert, admin_site=AdminSite())

        assert not admin.has_add_permission(request=None)
        assert not admin.has_delete_permission(request=None)
        assert "alert_message_ts" in admin.readonly_fields
